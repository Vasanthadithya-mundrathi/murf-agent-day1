"""
Day 5 - SDR Agent for Razorpay
Sales Development Representative that answers FAQs and captures leads.
"""
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

from dotenv import load_dotenv

# Load env from the backend directory
BACKEND_DIR = Path(__file__).parent.parent
load_dotenv(BACKEND_DIR / ".env.local")

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import murf, silero, deepgram, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("sdr_agent")
logger.setLevel(logging.INFO)

# Load company FAQ data
FAQ_PATH = BACKEND_DIR / "shared-data" / "razorpay_faq.json"
LEADS_DIR = BACKEND_DIR / "shared-data" / "leads"
LEADS_DIR.mkdir(exist_ok=True)

with open(FAQ_PATH, "r") as f:
    COMPANY_DATA = json.load(f)

# Format FAQ for the prompt
FAQ_TEXT = "\n".join([
    f"Q: {item['question']}\nA: {item['answer']}"
    for item in COMPANY_DATA["faq"]
])

PRODUCTS_TEXT = "\n".join([
    f"- {p['name']}: {p['description']} (Best for: {p['use_case']})"
    for p in COMPANY_DATA["products"]
])

PRICING_TEXT = f"""
Payment Gateway: {COMPANY_DATA['pricing']['payment_gateway']['domestic']} domestic, {COMPANY_DATA['pricing']['payment_gateway']['international']} international. No setup or annual fees.
Payment Links: {COMPANY_DATA['pricing']['payment_links']['fee']}
Razorpay X Banking: Starter (Free), Growth (₹499/month), Enterprise (Custom)
"""


@dataclass
class LeadInfo:
    """Lead information captured during the call"""
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    use_case: Optional[str] = None
    team_size: Optional[str] = None
    timeline: Optional[str] = None  # now / soon / later
    call_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    def is_complete(self) -> bool:
        """Check if we have minimum required info"""
        return bool(self.name and self.company and self.email)
    
    def missing_fields(self) -> list:
        """Return list of missing important fields"""
        missing = []
        if not self.name:
            missing.append("name")
        if not self.company:
            missing.append("company")
        if not self.email:
            missing.append("email")
        if not self.role:
            missing.append("role")
        if not self.use_case:
            missing.append("use_case")
        return missing


@dataclass 
class UserData:
    """Session data"""
    lead: LeadInfo = field(default_factory=LeadInfo)
    ctx: Optional[JobContext] = None
    conversation_ended: bool = False


# Type alias
RunContext_T = RunContext[UserData]


SDR_SYSTEM_PROMPT = f"""You are Robin, a friendly Sales Development Representative (SDR) for Razorpay.

## YOUR COMPANY
{COMPANY_DATA['company']['description']}

## PRODUCTS
{PRODUCTS_TEXT}

## PRICING
{PRICING_TEXT}

## FAQ KNOWLEDGE BASE
Use this to answer questions accurately. Don't make up information not in here:
{FAQ_TEXT}

## YOUR GOALS
1. Warmly greet visitors and understand what brought them here
2. Answer their questions about Razorpay using the FAQ
3. Naturally collect lead information during conversation
4. Provide helpful, accurate information

## LEAD INFORMATION TO COLLECT
Naturally work these into conversation (don't ask all at once):
- Name
- Company name
- Email address
- Role/Title
- Use case (what they want to use Razorpay for)
- Team size (approximate)
- Timeline (looking to start now, soon, or later)

## CONVERSATION STYLE
- Be warm, friendly, and professional
- Keep responses concise (2-3 sentences max)
- Ask ONE question at a time
- Listen and respond to what they say
- Don't be pushy about collecting info

## TOOLS
- Use save_lead_info to save lead details as you learn them
- Use end_call_summary when the user says goodbye or indicates they're done

## OPENING
"Hi! I'm Robin from Razorpay. Thanks for reaching out! What brings you here today - are you looking for a payment solution for your business?"
"""


def save_lead_to_file(lead: LeadInfo, room_name: str):
    """Save lead data to JSON file"""
    filename = f"lead_{room_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = LEADS_DIR / filename
    
    with open(filepath, "w") as f:
        json.dump(lead.to_dict(), f, indent=2)
    
    logger.info(f"Lead saved to {filepath}")
    return filepath


class SDRAgent(Agent):
    """SDR Agent for Razorpay"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=SDR_SYSTEM_PROMPT,
            stt=deepgram.STT(model="nova-3"),
            llm=openai.LLM(
                base_url="http://127.0.0.1:11434/v1",
                model="mistral:latest",
                api_key="ollama",
                temperature=0.7,
            ),
            tts=murf.TTS(voice="en-IN-natalie", style="Conversational"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
    
    async def on_enter(self) -> None:
        """Called when agent starts"""
        logger.info("SDR Agent started")
        userdata: UserData = self.session.userdata
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes({"agent": "SDRAgent"})
        self.session.generate_reply()
    
    @function_tool
    async def save_lead_info(
        self,
        context: RunContext_T,
        name: str = None,
        company: str = None,
        email: str = None,
        role: str = None,
        use_case: str = None,
        team_size: str = None,
        timeline: str = None,
    ) -> str:
        """
        Save lead information as you learn it during the conversation.
        Call this whenever the user shares any of these details.
        
        Args:
            name: The person's name
            company: Their company name
            email: Their email address
            role: Their job title/role
            use_case: What they want to use Razorpay for
            team_size: Approximate team or company size
            timeline: When they're looking to start (now/soon/later)
        """
        lead = context.userdata.lead
        
        if name:
            lead.name = name
            logger.info(f"Captured name: {name}")
        if company:
            lead.company = company
            logger.info(f"Captured company: {company}")
        if email:
            lead.email = email
            logger.info(f"Captured email: {email}")
        if role:
            lead.role = role
            logger.info(f"Captured role: {role}")
        if use_case:
            lead.use_case = use_case
            logger.info(f"Captured use_case: {use_case}")
        if team_size:
            lead.team_size = team_size
            logger.info(f"Captured team_size: {team_size}")
        if timeline:
            lead.timeline = timeline
            logger.info(f"Captured timeline: {timeline}")
        
        return "Lead info saved successfully."
    
    @function_tool
    async def end_call_summary(
        self,
        context: RunContext_T,
        summary: str,
    ) -> str:
        """
        Generate end-of-call summary when user indicates they're done.
        Call this when user says goodbye, thanks, that's all, etc.
        
        Args:
            summary: A brief summary of what the lead needs and next steps
        """
        userdata = context.userdata
        lead = userdata.lead
        lead.summary = summary
        userdata.conversation_ended = True
        
        # Save to file
        room_name = userdata.ctx.room.name if userdata.ctx else "unknown"
        filepath = save_lead_to_file(lead, room_name)
        
        # Build verbal summary
        parts = []
        if lead.name:
            parts.append(f"{lead.name}")
        if lead.company:
            parts.append(f"from {lead.company}")
        if lead.use_case:
            parts.append(f"interested in {lead.use_case}")
        if lead.timeline:
            parts.append(f"timeline: {lead.timeline}")
        
        verbal_summary = ", ".join(parts) if parts else "Lead details captured"
        
        logger.info(f"Call ended. Summary: {verbal_summary}")
        logger.info(f"Lead data saved to: {filepath}")
        
        return f"Summary saved. Lead: {verbal_summary}"


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the SDR Agent"""
    logger.info(f"Starting SDR Agent in room {ctx.room.name}")
    
    await ctx.connect()
    
    # Initialize userdata
    userdata = UserData(ctx=ctx)
    
    # Create SDR agent
    sdr = SDRAgent()
    
    # Create session with userdata
    session = AgentSession[UserData](userdata=userdata)
    
    # Start the agent
    await session.start(
        agent=sdr,
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
