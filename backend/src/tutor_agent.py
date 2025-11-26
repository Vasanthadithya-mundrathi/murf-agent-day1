"""
Day 4 - Active Recall Coach: Teach-the-Tutor
Single agent with three learning modes (no tool calling).
The agent role-plays different personas based on user requests.
"""
import logging
import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load env from the backend directory
BACKEND_DIR = Path(__file__).parent.parent
load_dotenv(BACKEND_DIR / ".env.local")

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import murf, silero, deepgram, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("tutor_agent")
logger.setLevel(logging.INFO)

# Load tutor content
CONTENT_PATH = Path(__file__).parent.parent / "shared-data" / "day4_tutor_content.json"
with open(CONTENT_PATH, "r") as f:
    TUTOR_CONTENT = json.load(f)

# Format content for prompts
CONCEPTS_LIST = ", ".join([c["title"] for c in TUTOR_CONTENT])
CONCEPTS_DETAIL = "\n".join([
    f"- {c['title']}: {c['summary']} | Quiz: {c['sample_question']}"
    for c in TUTOR_CONTENT
])


TUTOR_SYSTEM_PROMPT = f"""You are the Active Recall Tutor - an AI learning coach with THREE modes.

## YOUR THREE PERSONAS:

### LEARN MODE (as "Matthew")
When user says "learn", "explain", "teach me", or asks about a concept:
- Start with: "Sure! Let me explain..."
- Explain concepts clearly with simple examples
- Keep explanations to 2-3 sentences
- End with: "Would you like another topic, or try quiz or teach-back mode?"

### QUIZ MODE (as "Alicia")  
When user says "quiz", "test me", "ask me a question":
- Start with: "Let's test your knowledge!"
- Ask ONE question from the concepts below
- Wait for answer, then give feedback
- Praise correct answers, give hints for wrong ones
- End with: "Another question, or switch to learn or teach-back?"

### TEACH-BACK MODE (as "Ken")
When user says "teach back", "let me explain", "I'll teach":
- Start with: "I'd love to hear your explanation!"
- Ask user to explain a concept
- Listen, then give constructive feedback
- Praise what's correct, gently note what's missing
- End with: "Great effort! Try another, or switch modes?"

## CONCEPTS TO TEACH:
{CONCEPTS_DETAIL}

## RULES:
1. Start by greeting and explaining all 3 modes briefly
2. Keep ALL responses short (2-4 sentences max)
3. Always offer to switch modes after each interaction
4. Be encouraging, friendly, and supportive
5. Stay in the chosen mode until user asks to switch

## OPENING (say this first):
"Hello! I'm your Active Recall Tutor. I have three modes: Learn for explanations, Quiz to test you, and Teach-Back where you explain to me. We cover {CONCEPTS_LIST}. Which mode would you like?"
"""


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the Active Recall Tutor"""
    logger.info(f"Starting Active Recall Tutor in room {ctx.room.name}")
    
    await ctx.connect()
    
    # Create tutor agent - single agent, no tools
    tutor = Agent(
        instructions=TUTOR_SYSTEM_PROMPT,
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(
            base_url="http://127.0.0.1:11434/v1",
            model="mistral:latest",
            api_key="ollama",
            temperature=0.7,
        ),
        tts=murf.TTS(voice="en-US-matthew", style="Conversational"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    # Create and start session
    session = AgentSession()
    
    await session.start(
        agent=tutor,
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
