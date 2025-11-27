"""
Day 6 - Fraud Alert Voice Agent: LEO
Bank fraud detection agent that verifies transactions with customers.
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

from dotenv import load_dotenv

# Load env from the backend directory
BACKEND_DIR = Path(__file__).parent.parent
load_dotenv(BACKEND_DIR / ".env.local")

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import murf, silero, deepgram, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("fraud_agent")
logger.setLevel(logging.INFO)

# Database path
DB_PATH = BACKEND_DIR / "shared-data" / "fraud_cases.json"


class CaseStatus(str, Enum):
    PENDING = "pending_review"
    SAFE = "confirmed_safe"
    FRAUD = "confirmed_fraud"
    VERIFICATION_FAILED = "verification_failed"


def load_database() -> Dict[str, Any]:
    """Load fraud cases from JSON database"""
    with open(DB_PATH, "r") as f:
        return json.load(f)


def save_database(data: Dict[str, Any]) -> None:
    """Save fraud cases to JSON database"""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Database updated successfully")


def get_case_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Find a fraud case by username"""
    db = load_database()
    username_lower = username.lower().strip()
    for case in db["cases"]:
        if case["user_name"].lower() == username_lower:
            return case
    return None


def update_case_status(case_id: str, status: str, outcome_note: str) -> bool:
    """Update a case's status and outcome in the database"""
    db = load_database()
    for case in db["cases"]:
        if case["case_id"] == case_id:
            case["status"] = status
            case["outcome_note"] = outcome_note
            case["resolved_at"] = datetime.now().isoformat()
            save_database(db)
            logger.info(f"Case {case_id} updated: status={status}")
            return True
    return False


@dataclass
class SessionData:
    """Session state for fraud verification"""
    ctx: Optional[JobContext] = None
    current_case: Optional[Dict[str, Any]] = None
    verified: bool = False
    verification_attempts: int = 0
    call_completed: bool = False


# Type alias
RunContext_T = RunContext[SessionData]


FRAUD_AGENT_PROMPT = """You are LEO, a professional Fraud Detection Agent for SecureBank India.

## YOUR ROLE
You are calling customers about suspicious transactions detected on their accounts.
Be calm, professional, and reassuring. Customers may be worried - help them feel secure.

## IMPORTANT SECURITY RULES
- NEVER ask for full card numbers, PINs, CVV, or passwords
- NEVER ask for OTPs or complete account numbers
- Only verify using the security question from the database
- If verification fails 2 times, end the call politely

## CALL FLOW

### Step 1: Introduction
Start with: "Hello, this is LEO from SecureBank India's Fraud Detection Unit. Am I speaking with [customer name]? I'm calling regarding some unusual activity we've noticed on your account."

### Step 2: Get Username (if not loaded)
Ask for their username to look up their case. Use the lookup_fraud_case tool.

### Step 3: Verification
Once case is loaded, verify the customer:
- "For security purposes, I need to verify your identity."
- "Could you please answer your security question: [question from database]?"
- Use verify_customer tool to check the answer
- If wrong, give ONE more chance
- If still wrong, use mark_verification_failed tool

### Step 4: Explain Suspicious Transaction (only if verified)
Read the transaction details:
- "We've detected a suspicious transaction on your [card_type] ending in [card_ending]."
- "On [transaction_time], a purchase of [amount] was attempted at [transaction_name]."
- "This transaction originated from [transaction_location] via [transaction_source]."

### Step 5: Ask for Confirmation
- "Did you authorize this transaction? Please say yes if you made this purchase, or no if you did not."

### Step 6: Take Action
Based on response:
- If YES (customer made it): Use mark_case_safe tool
  - "Thank you for confirming. I've marked this transaction as legitimate. Your card will remain active."
- If NO (fraud): Use mark_case_fraud tool
  - "I understand. I've immediately blocked your card to prevent further unauthorized use. A new card will be sent within 3-5 business days. You won't be charged for this fraudulent transaction."

### Step 7: End Call
- Thank them and wish them a good day
- "Thank you for your time. If you have any questions, call our 24/7 helpline. Have a secure day!"

## CONVERSATION STYLE
- Be professional but warm
- Keep responses concise (2-3 sentences)
- Be patient if the customer is confused or worried
- Reassure them that their account is being protected
"""


class FraudAgent(Agent):
    """LEO - Fraud Detection Agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=FRAUD_AGENT_PROMPT,
            stt=deepgram.STT(model="nova-3"),
            llm=openai.LLM(
                base_url="http://127.0.0.1:11434/v1",
                model="mistral:latest",
                api_key="ollama",
                temperature=0.7,
            ),
            tts=murf.TTS(voice="en-IN-arjun", style="Conversational"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
    
    async def on_enter(self) -> None:
        """Called when agent starts"""
        logger.info("LEO Fraud Agent started")
        userdata: SessionData = self.session.userdata
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes({"agent": "FraudAgent-LEO"})
        self.session.generate_reply()
    
    @function_tool
    async def lookup_fraud_case(
        self,
        context: RunContext_T,
        username: str,
    ) -> str:
        """
        Look up a fraud case by username. Call this when the customer provides their username.
        
        Args:
            username: The customer's username to look up their fraud case
        """
        case = get_case_by_username(username)
        
        if not case:
            logger.info(f"No case found for username: {username}")
            return f"No pending fraud case found for username '{username}'. Please verify the username and try again."
        
        if case["status"] != CaseStatus.PENDING:
            return f"The case for {case['full_name']} has already been resolved with status: {case['status']}."
        
        # Store case in session
        context.userdata.current_case = case
        logger.info(f"Loaded case {case['case_id']} for {case['full_name']}")
        
        return f"""Case loaded successfully for {case['full_name']}.
Card: {case['card_type']} ending in {case['card_ending']}
Security Question: {case['security_question']}
Transaction: {case['transaction_amount']} at {case['transaction_name']}
Location: {case['transaction_location']}
Time: {case['transaction_time']}

Now verify the customer by asking the security question."""
    
    @function_tool
    async def verify_customer(
        self,
        context: RunContext_T,
        answer: str,
    ) -> str:
        """
        Verify the customer's identity using their security answer.
        Call this after the customer answers the security question.
        
        Args:
            answer: The customer's answer to the security question
        """
        session = context.userdata
        case = session.current_case
        
        if not case:
            return "Error: No case loaded. Please look up the customer's case first."
        
        session.verification_attempts += 1
        correct_answer = case["security_answer"].lower().strip()
        given_answer = answer.lower().strip()
        
        if given_answer == correct_answer:
            session.verified = True
            logger.info(f"Customer verified for case {case['case_id']}")
            return f"""Verification SUCCESSFUL for {case['full_name']}.
You may now explain the suspicious transaction:
- Amount: {case['transaction_amount']}
- Merchant: {case['transaction_name']}
- Source: {case['transaction_source']}
- Location: {case['transaction_location']}
- Time: {case['transaction_time']}
- Card: {case['card_type']} ending in {case['card_ending']}

Ask if they authorized this transaction."""
        
        if session.verification_attempts >= 2:
            return "Verification FAILED twice. Use mark_verification_failed to end the call securely."
        
        return f"Incorrect answer. Attempt {session.verification_attempts}/2. Ask them to try again."
    
    @function_tool
    async def mark_case_safe(
        self,
        context: RunContext_T,
    ) -> str:
        """
        Mark the current case as safe/legitimate when customer confirms they made the transaction.
        Call this when the customer says YES they made the transaction.
        """
        session = context.userdata
        case = session.current_case
        
        if not case:
            return "Error: No case loaded."
        
        if not session.verified:
            return "Error: Customer not verified. Cannot update case status."
        
        outcome = f"Customer {case['full_name']} confirmed transaction as legitimate on {datetime.now().strftime('%Y-%m-%d %H:%M')}. Card remains active."
        
        success = update_case_status(case["case_id"], CaseStatus.SAFE, outcome)
        session.call_completed = True
        
        if success:
            logger.info(f"Case {case['case_id']} marked as SAFE")
            return f"Case {case['case_id']} marked as CONFIRMED SAFE. Transaction verified as legitimate. Thank the customer and end the call."
        
        return "Error updating case status."
    
    @function_tool
    async def mark_case_fraud(
        self,
        context: RunContext_T,
    ) -> str:
        """
        Mark the current case as fraudulent and block the card.
        Call this when the customer says NO they did not make the transaction.
        """
        session = context.userdata
        case = session.current_case
        
        if not case:
            return "Error: No case loaded."
        
        if not session.verified:
            return "Error: Customer not verified. Cannot update case status."
        
        outcome = f"Customer {case['full_name']} denied transaction on {datetime.now().strftime('%Y-%m-%d %H:%M')}. Card ending {case['card_ending']} BLOCKED. Dispute raised. New card to be issued."
        
        success = update_case_status(case["case_id"], CaseStatus.FRAUD, outcome)
        session.call_completed = True
        
        if success:
            logger.info(f"Case {case['case_id']} marked as FRAUD - Card blocked")
            return f"""Case {case['case_id']} marked as CONFIRMED FRAUD.
Actions taken:
- Card ending {case['card_ending']} has been BLOCKED
- Fraudulent transaction of {case['transaction_amount']} reversed
- New card will be issued in 3-5 business days
- Dispute case opened

Inform the customer of these actions and end the call."""
        
        return "Error updating case status."
    
    @function_tool
    async def mark_verification_failed(
        self,
        context: RunContext_T,
    ) -> str:
        """
        Mark the case as verification failed when customer cannot verify identity.
        Call this after 2 failed verification attempts.
        """
        session = context.userdata
        case = session.current_case
        
        if not case:
            return "Error: No case loaded."
        
        outcome = f"Verification failed after {session.verification_attempts} attempts on {datetime.now().strftime('%Y-%m-%d %H:%M')}. Case requires manual review."
        
        success = update_case_status(case["case_id"], CaseStatus.VERIFICATION_FAILED, outcome)
        session.call_completed = True
        
        if success:
            logger.info(f"Case {case['case_id']} marked as VERIFICATION_FAILED")
            return f"""Case {case['case_id']} marked as VERIFICATION FAILED.
For security, we cannot proceed without proper verification.
Politely inform the customer:
- They can call back with proper identification
- Or visit their nearest SecureBank branch with ID proof
- Their account is temporarily secured for their protection
End the call professionally."""
        
        return "Error updating case status."


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the Fraud Agent"""
    logger.info(f"Starting LEO Fraud Agent in room {ctx.room.name}")
    
    await ctx.connect()
    
    # Initialize session data
    session_data = SessionData(ctx=ctx)
    
    # Create fraud agent
    leo = FraudAgent()
    
    # Create session
    session = AgentSession[SessionData](userdata=session_data)
    
    # Start the agent
    await session.start(
        agent=leo,
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
