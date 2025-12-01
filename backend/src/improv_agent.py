"""
Day 10: Voice Improv Battle - Game Show Host Agent
MAX - The AI Improv Host
"""

import json
import random
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from livekit.agents import Agent, AgentSession, RunContext, function_tool, RoomInputOptions
from livekit.agents.llm import ChatContext
from livekit.plugins import deepgram, openai, murf

# Paths
SCENARIOS_PATH = Path(__file__).parent.parent / "shared-data" / "improv_scenarios.json"


@dataclass
class RoundResult:
    """Result of a single improv round"""
    round_number: int
    scenario_title: str
    scenario_setup: str
    player_performance: str
    host_reaction: str
    tone: str  # positive, mixed, critical


@dataclass
class ImprovState:
    """Game state for improv battle"""
    player_name: str = ""
    current_round: int = 0
    max_rounds: int = 4
    phase: str = "intro"  # intro, awaiting_improv, reacting, closing, done
    rounds: list[RoundResult] = field(default_factory=list)
    available_scenarios: list = field(default_factory=list)
    current_scenario: dict = field(default_factory=dict)
    game_started: bool = False
    show_data: dict = field(default_factory=dict)


def load_scenarios() -> dict:
    """Load improv scenarios from JSON"""
    if SCENARIOS_PATH.exists():
        with open(SCENARIOS_PATH, "r") as f:
            return json.load(f)
    return {"scenarios": [], "show_info": {}}


def get_random_scenario(state: ImprovState) -> dict:
    """Get a random scenario that hasn't been used yet"""
    if not state.available_scenarios:
        return {}
    scenario = random.choice(state.available_scenarios)
    state.available_scenarios.remove(scenario)
    return scenario


def determine_reaction_tone() -> str:
    """Randomly determine the tone of host's reaction"""
    weights = [0.4, 0.35, 0.25]  # positive, mixed, critical
    return random.choices(["positive", "mixed", "critical"], weights=weights)[0]


# ============== FUNCTION TOOLS ==============

@function_tool
def start_game(ctx: RunContext[ImprovState], player_name: str) -> str:
    """
    Start the improv battle game with the player's name.
    
    Args:
        player_name: The name of the contestant
    """
    ctx.userdata.player_name = player_name
    ctx.userdata.game_started = True
    ctx.userdata.phase = "awaiting_improv"
    ctx.userdata.current_round = 1
    
    # Get first scenario
    scenario = get_random_scenario(ctx.userdata)
    ctx.userdata.current_scenario = scenario
    
    show_name = ctx.userdata.show_data.get("show_info", {}).get("name", "Improv Battle")
    
    return f"""
🎭 GAME STARTED!

Player: {player_name}
Show: {show_name}
Total Rounds: {ctx.userdata.max_rounds}

ROUND 1 SCENARIO: "{scenario.get('title', 'Unknown')}"

{scenario.get('setup', 'No scenario available')}

Tell {player_name} to begin their improv performance!
"""


@function_tool
def get_current_scenario(ctx: RunContext[ImprovState]) -> str:
    """
    Get the current scenario details for the ongoing round.
    """
    if not ctx.userdata.current_scenario:
        return "No active scenario. Start the game first!"
    
    scenario = ctx.userdata.current_scenario
    return f"""
ROUND {ctx.userdata.current_round} SCENARIO: "{scenario.get('title', '')}"

{scenario.get('setup', '')}

Difficulty: {scenario.get('difficulty', 'medium')}
Tags: {', '.join(scenario.get('tags', []))}
"""


@function_tool
def record_performance_and_react(ctx: RunContext[ImprovState], 
                                 performance_summary: str,
                                 reaction: str) -> str:
    """
    Record the player's performance and the host's reaction for the current round.
    Call this after the player finishes their improv.
    
    Args:
        performance_summary: Brief summary of what the player did in their improv
        reaction: The host's reaction/feedback to give
    """
    tone = determine_reaction_tone()
    
    round_result = RoundResult(
        round_number=ctx.userdata.current_round,
        scenario_title=ctx.userdata.current_scenario.get('title', ''),
        scenario_setup=ctx.userdata.current_scenario.get('setup', ''),
        player_performance=performance_summary,
        host_reaction=reaction,
        tone=tone
    )
    ctx.userdata.rounds.append(round_result)
    
    return f"""
📝 ROUND {ctx.userdata.current_round} RECORDED

Performance: {performance_summary}
Reaction Tone: {tone}

Host should now deliver the reaction with a {tone} tone.
"""


@function_tool
def advance_to_next_round(ctx: RunContext[ImprovState]) -> str:
    """
    Move to the next round after the host has reacted to the current performance.
    """
    ctx.userdata.current_round += 1
    
    if ctx.userdata.current_round > ctx.userdata.max_rounds:
        ctx.userdata.phase = "closing"
        return f"""
🏁 ALL ROUNDS COMPLETE!

Completed: {ctx.userdata.max_rounds} rounds
Phase: Closing

Time for the final summary and goodbye!
"""
    
    # Get next scenario
    scenario = get_random_scenario(ctx.userdata)
    ctx.userdata.current_scenario = scenario
    ctx.userdata.phase = "awaiting_improv"
    
    return f"""
➡️ ADVANCING TO ROUND {ctx.userdata.current_round}

NEW SCENARIO: "{scenario.get('title', '')}"

{scenario.get('setup', '')}

Announce the new scenario to the player!
"""


@function_tool
def get_game_summary(ctx: RunContext[ImprovState]) -> str:
    """
    Get a summary of all rounds played for the final closing.
    """
    if not ctx.userdata.rounds:
        return "No rounds played yet."
    
    lines = [
        f"🎭 IMPROV BATTLE SUMMARY for {ctx.userdata.player_name}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Rounds Played: {len(ctx.userdata.rounds)}",
        ""
    ]
    
    positive_count = sum(1 for r in ctx.userdata.rounds if r.tone == "positive")
    mixed_count = sum(1 for r in ctx.userdata.rounds if r.tone == "mixed")
    critical_count = sum(1 for r in ctx.userdata.rounds if r.tone == "critical")
    
    lines.append("Round Highlights:")
    for r in ctx.userdata.rounds:
        emoji = "⭐" if r.tone == "positive" else "👍" if r.tone == "mixed" else "📝"
        lines.append(f"{emoji} Round {r.round_number}: {r.scenario_title}")
        lines.append(f"   Performance: {r.player_performance[:100]}...")
    
    lines.append("")
    lines.append(f"Feedback Breakdown: {positive_count} stellar, {mixed_count} good, {critical_count} needs work")
    
    # Suggest a player style
    styles = ctx.userdata.show_data.get("player_styles", [
        "The Improviser - You brought creativity to every scene!"
    ])
    player_style = random.choice(styles)
    
    lines.append(f"\nPlayer Style: {player_style}")
    
    return "\n".join(lines)


@function_tool
def end_game(ctx: RunContext[ImprovState]) -> str:
    """
    End the improv battle game session.
    """
    ctx.userdata.phase = "done"
    
    return f"""
🎬 GAME ENDED

Player: {ctx.userdata.player_name}
Rounds Completed: {len(ctx.userdata.rounds)}/{ctx.userdata.max_rounds}
Final Phase: Done

Thank the player and sign off!
"""


@function_tool
def get_current_state(ctx: RunContext[ImprovState]) -> str:
    """
    Get the current game state for reference.
    """
    return f"""
📊 CURRENT GAME STATE

Player: {ctx.userdata.player_name or 'Not set'}
Phase: {ctx.userdata.phase}
Current Round: {ctx.userdata.current_round}/{ctx.userdata.max_rounds}
Rounds Completed: {len(ctx.userdata.rounds)}
Game Started: {ctx.userdata.game_started}
Scenarios Remaining: {len(ctx.userdata.available_scenarios)}
"""


# ============== HOST AGENT SETUP ==============

IMPROV_HOST_INSTRUCTIONS = """You are MAX, the charismatic and witty host of "IMPROV BATTLE" - a voice-first improv game show!

## Your Personality
- High-energy, theatrical, and entertaining
- Quick-witted with a flair for dramatic announcements
- You give HONEST feedback - not always positive!
- Supportive but not sycophantic - you're a real critic
- Think: game show host meets improv teacher

## Your Voice Style
- Use dramatic pauses and emphasis
- React genuinely - laugh when it's funny, be honest when it falls flat
- Vary your energy: sometimes excited, sometimes thoughtfully critical
- Be encouraging but authentic

## Game Structure
1. **INTRO**: Welcome the player, explain the rules, get their name
2. **ROUNDS** (4 total): For each round:
   - Announce the scenario dramatically
   - Say "BEGIN!" or similar to start them
   - Listen to their improv
   - When they finish (pause, "end scene", or seem done), REACT
   - Give feedback (use varied tones - not always positive!)
   - Move to next round
3. **CLOSING**: Summarize their performance, give a player style, thank them

## How to React to Performances
Vary your reactions! Not everything is amazing:
- **STELLAR** (40%): "That was BRILLIANT! The way you..."
- **GOOD** (35%): "Okay, I liked where you were going, but..."
- **NEEDS WORK** (25%): "Hmm, that felt a bit rushed/flat..."

Always be constructive, never mean. Light teasing is okay!

## Key Phrases to Listen For
- "End scene" / "I'm done" / "That's it" = They're finished
- "Stop" / "End game" / "I want to quit" = End early gracefully
- Long pause after speaking = They might be done

## Important Rules
- ALWAYS use the tools to track game state
- Call start_game when you get their name
- Call record_performance_and_react after each performance
- Call advance_to_next_round to get the next scenario
- Call get_game_summary before closing
- Keep the energy up but stay genuine!

## Starting the Show
Begin with a dramatic intro:
"WELCOME to IMPROV BATTLE! I'm your host MAX, and tonight, we're going to test your quick wit, your creativity, and your ability to commit to the ABSURD! Are you ready to play? First, tell me - what's your name, brave improviser?"
"""


if __name__ == "__main__":
    from livekit.agents import WorkerOptions, cli
    from livekit.plugins import silero

    async def entrypoint(ctx: AgentSession):
        # Initialize game state
        game_state = ImprovState()
        
        # Load scenarios
        show_data = load_scenarios()
        game_state.show_data = show_data
        game_state.available_scenarios = show_data.get("scenarios", []).copy()
        game_state.max_rounds = show_data.get("show_info", {}).get("max_rounds", 4)

        # Configure LLM
        llm = openai.LLM.with_ollama(
            model="mistral",
            base_url="http://127.0.0.1:11434/v1",
        )

        # Configure TTS - Energetic host voice
        tts = murf.TTS(
            voice="en-US-terrell",  # Energetic American male voice
            model="GEN2",
            sample_rate=24000,
        )

        # Configure STT
        stt = deepgram.STT(model="nova-3", language="en")

        # Configure VAD
        vad = silero.VAD.load()

        # Build initial context
        initial_ctx = ChatContext()
        initial_ctx.add_message(
            role="system",
            content=f"""{IMPROV_HOST_INSTRUCTIONS}

Available scenarios: {len(game_state.available_scenarios)}
Max rounds: {game_state.max_rounds}
"""
        )

        # Create agent with game tools
        agent = Agent(
            instructions=IMPROV_HOST_INSTRUCTIONS,
            chat_ctx=initial_ctx,
            llm=llm,
            tts=tts,
            stt=stt,
            vad=vad,
            tools=[
                start_game,
                get_current_scenario,
                record_performance_and_react,
                advance_to_next_round,
                get_game_summary,
                end_game,
                get_current_state
            ]
        )

        # Start session
        await ctx.start(
            agent=agent,
            room_input_options=RoomInputOptions(),
            userdata=game_state
        )

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
