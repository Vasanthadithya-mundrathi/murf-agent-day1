"""
Day 8: Voice Game Master - D&D-Style Adventure Agent
Universe: The Witcher - Dark Fantasy Monster Hunting
"""

import json
import random
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from livekit.agents import Agent, AgentSession, RunContext, function_tool, RoomInputOptions
from livekit.agents.llm import ChatContext
from livekit.plugins import deepgram, openai, murf


@dataclass
class PlayerStats:
    """Player character stats"""
    name: str = "Witcher"
    health: int = 100
    max_health: int = 100
    strength: int = 15
    agility: int = 14
    signs: int = 12  # Magic ability
    gold: int = 50
    inventory: list = field(default_factory=lambda: ["Steel Sword", "Silver Sword", "2 Swallow Potions"])
    status: str = "Healthy"


@dataclass
class GameState:
    """Full game state including world and player"""
    player: PlayerStats = field(default_factory=PlayerStats)
    current_location: str = "Crossroads Inn"
    current_scene: str = "The tavern is dimly lit, filled with the smell of ale and woodsmoke."
    npcs_met: list = field(default_factory=list)
    quests_active: list = field(default_factory=list)
    quests_completed: list = field(default_factory=list)
    events: list = field(default_factory=list)
    turn_count: int = 0
    story_arc: str = "beginning"  # beginning, rising, climax, resolution


# ============== GAME MECHANICS ==============

def roll_dice(sides: int = 20, modifier: int = 0) -> tuple[int, int]:
    """Roll a dice and return (raw_roll, modified_result)"""
    roll = random.randint(1, sides)
    return roll, roll + modifier


def check_outcome(roll: int, difficulty: int = 12) -> str:
    """Determine outcome based on roll vs difficulty"""
    if roll >= difficulty + 5:
        return "critical_success"
    elif roll >= difficulty:
        return "success"
    elif roll >= difficulty - 5:
        return "partial_success"
    else:
        return "failure"


def get_stat_modifier(stat: int) -> int:
    """Convert stat to D&D-style modifier"""
    return (stat - 10) // 2


# ============== FUNCTION TOOLS ==============

@function_tool
def roll_skill_check(ctx: RunContext[GameState], skill: str, difficulty: str = "normal") -> str:
    """
    Perform a skill check with dice roll when the player attempts something risky.
    
    Args:
        skill: The skill to check - 'strength', 'agility', or 'signs' (magic)
        difficulty: How hard the task is - 'easy', 'normal', 'hard', 'very_hard'
    """
    player = ctx.userdata.player
    
    # Get stat value
    stat_value = getattr(player, skill.lower(), 10)
    modifier = get_stat_modifier(stat_value)
    
    # Set difficulty class
    dc_map = {"easy": 8, "normal": 12, "hard": 15, "very_hard": 18}
    dc = dc_map.get(difficulty.lower(), 12)
    
    # Roll!
    raw_roll, total = roll_dice(20, modifier)
    outcome = check_outcome(total, dc)
    
    outcome_text = {
        "critical_success": "CRITICAL SUCCESS! Exceptional result!",
        "success": "SUCCESS! You manage to do it.",
        "partial_success": "PARTIAL SUCCESS. You succeed, but with a complication.",
        "failure": "FAILURE. Things don't go as planned."
    }
    
    return f"🎲 {skill.upper()} CHECK (DC {dc}): Rolled {raw_roll} + {modifier} = {total}. {outcome_text[outcome]}"


@function_tool
def update_player_health(ctx: RunContext[GameState], change: int, reason: str) -> str:
    """
    Update player's health when they take damage or heal.
    
    Args:
        change: Amount to change (negative for damage, positive for healing)
        reason: What caused the health change
    """
    player = ctx.userdata.player
    old_health = player.health
    player.health = max(0, min(player.max_health, player.health + change))
    
    # Update status
    if player.health <= 0:
        player.status = "Dead"
    elif player.health <= 25:
        player.status = "Critical"
    elif player.health <= 50:
        player.status = "Injured"
    else:
        player.status = "Healthy"
    
    if change < 0:
        return f"💔 Took {abs(change)} damage from {reason}. Health: {old_health} → {player.health}. Status: {player.status}"
    else:
        return f"💚 Healed {change} HP from {reason}. Health: {old_health} → {player.health}. Status: {player.status}"


@function_tool
def add_to_inventory(ctx: RunContext[GameState], item: str) -> str:
    """
    Add an item to player's inventory.
    
    Args:
        item: Name of the item to add
    """
    ctx.userdata.player.inventory.append(item)
    return f"📦 Added '{item}' to inventory. You now have: {', '.join(ctx.userdata.player.inventory)}"


@function_tool
def remove_from_inventory(ctx: RunContext[GameState], item: str) -> str:
    """
    Remove an item from player's inventory.
    
    Args:
        item: Name of the item to remove
    """
    inventory = ctx.userdata.player.inventory
    
    # Find item (case-insensitive partial match)
    for i, inv_item in enumerate(inventory):
        if item.lower() in inv_item.lower():
            removed = inventory.pop(i)
            return f"📦 Removed '{removed}' from inventory."
    
    return f"You don't have '{item}' in your inventory."


@function_tool
def check_inventory(ctx: RunContext[GameState]) -> str:
    """
    Check what items the player has in their inventory.
    """
    player = ctx.userdata.player
    inv = player.inventory
    
    if not inv:
        return "Your inventory is empty."
    
    return f"🎒 INVENTORY ({len(inv)} items): {', '.join(inv)}. Gold: {player.gold} crowns."


@function_tool
def get_player_status(ctx: RunContext[GameState]) -> str:
    """
    Get the player's current stats and condition.
    """
    p = ctx.userdata.player
    return f"""
⚔️ WITCHER STATUS:
• Health: {p.health}/{p.max_health} ({p.status})
• Strength: {p.strength} (modifier: {get_stat_modifier(p.strength):+d})
• Agility: {p.agility} (modifier: {get_stat_modifier(p.agility):+d})
• Signs: {p.signs} (modifier: {get_stat_modifier(p.signs):+d})
• Gold: {p.gold} crowns
• Location: {ctx.userdata.current_location}
"""


@function_tool
def update_location(ctx: RunContext[GameState], new_location: str, description: str) -> str:
    """
    Move the player to a new location.
    
    Args:
        new_location: Name of the new location
        description: Description of the new location
    """
    old_location = ctx.userdata.current_location
    ctx.userdata.current_location = new_location
    ctx.userdata.current_scene = description
    ctx.userdata.events.append(f"Traveled from {old_location} to {new_location}")
    
    return f"📍 Moved to {new_location}. {description}"


@function_tool
def record_event(ctx: RunContext[GameState], event: str, is_major: bool = False) -> str:
    """
    Record an important event in the game's history.
    
    Args:
        event: Description of what happened
        is_major: Whether this is a major story event
    """
    ctx.userdata.events.append(event)
    ctx.userdata.turn_count += 1
    
    # Update story arc based on events
    turn = ctx.userdata.turn_count
    if turn >= 12:
        ctx.userdata.story_arc = "resolution"
    elif turn >= 8:
        ctx.userdata.story_arc = "climax"
    elif turn >= 4:
        ctx.userdata.story_arc = "rising"
    
    if is_major:
        return f"📜 MAJOR EVENT RECORDED: {event}. Story arc: {ctx.userdata.story_arc}"
    return f"Event noted: {event}"


@function_tool
def add_quest(ctx: RunContext[GameState], quest_name: str, description: str) -> str:
    """
    Add a new quest to the player's quest log.
    
    Args:
        quest_name: Name of the quest
        description: What the player needs to do
    """
    quest = {"name": quest_name, "description": description, "status": "active"}
    ctx.userdata.quests_active.append(quest)
    return f"📋 NEW QUEST: {quest_name} - {description}"


@function_tool
def complete_quest(ctx: RunContext[GameState], quest_name: str, reward_gold: int = 0) -> str:
    """
    Mark a quest as completed and give rewards.
    
    Args:
        quest_name: Name of the quest to complete
        reward_gold: Gold reward for completing the quest
    """
    for i, quest in enumerate(ctx.userdata.quests_active):
        if quest_name.lower() in quest["name"].lower():
            completed = ctx.userdata.quests_active.pop(i)
            completed["status"] = "completed"
            ctx.userdata.quests_completed.append(completed)
            ctx.userdata.player.gold += reward_gold
            return f"✅ QUEST COMPLETED: {completed['name']}! Earned {reward_gold} gold. Total gold: {ctx.userdata.player.gold}"
    
    return f"Quest '{quest_name}' not found in active quests."


@function_tool
def meet_npc(ctx: RunContext[GameState], npc_name: str, role: str, attitude: str) -> str:
    """
    Record meeting an NPC.
    
    Args:
        npc_name: Name of the NPC
        role: Their role (e.g., 'village elder', 'mysterious stranger', 'monster')
        attitude: Their attitude toward player (friendly, neutral, hostile)
    """
    npc = {"name": npc_name, "role": role, "attitude": attitude}
    ctx.userdata.npcs_met.append(npc)
    return f"👤 Met {npc_name} ({role}). Attitude: {attitude}"


# ============== GAME MASTER AGENT ==============

GAME_MASTER_INSTRUCTIONS = """You are a GAME MASTER running an interactive voice adventure set in THE WITCHER universe - a dark fantasy world of monster hunters, magic, and moral ambiguity.

## Your Role
You are the narrator and world. You describe scenes vividly, voice NPCs dramatically, and guide the player through a dangerous adventure. You speak as if telling an epic tale.

## The Setting
The player is a Witcher - a mutated monster hunter with supernatural abilities. They've arrived at a remote village plagued by a mysterious creature. The villagers are desperate and fearful.

## Starting Scene
The player enters the Crossroads Inn on a stormy night. Rain hammers the thatched roof. Inside, fearful villagers huddle around a fire, whispering about disappearances in the forest. The innkeeper, a grizzled man named Yorick, approaches...

## Your Voice & Style
- Dramatic, atmospheric narration ("The shadows seem to crawl along the walls...")
- Distinct NPC voices (gruff innkeeper, frightened villagers, mysterious stranger)
- Always end with "What do you do, Witcher?" or similar prompt for action
- Keep responses focused and conversational (2-4 sentences for descriptions, then ask for action)
- Build tension toward a climax around turns 8-12

## Game Mechanics
- Use roll_skill_check for risky actions (combat, acrobatics, magic)
- Update health when player takes damage or uses potions
- Track inventory changes (picking up items, using potions)
- Record major events and NPC meetings
- Add quests when NPCs give objectives

## Story Arc (guide the pacing)
1. **Beginning (turns 1-3)**: Introduce the mystery, meet key NPCs, gather information
2. **Rising (turns 4-7)**: Investigation, clues, minor dangers, build tension
3. **Climax (turns 8-11)**: Confront the monster/villain, major combat, high stakes
4. **Resolution (turns 12+)**: Aftermath, rewards, consequences of choices

## Important Rules
- The player's choices MATTER - honor their decisions
- Don't kill the player unfairly - make death meaningful
- If they ask about stats/inventory, use the appropriate tool
- Keep combat cinematic, not turn-based - describe action dramatically
- Incorporate The Witcher themes: moral grey areas, monster contracts, silver vs steel

## Starting the Adventure
Describe the stormy inn, introduce Yorick the innkeeper who tells of children disappearing in the Black Forest. He offers 200 gold for the monster's head. Then ask: "What do you do, Witcher?"
"""


if __name__ == "__main__":
    from livekit.agents import WorkerOptions, cli
    from livekit.plugins import silero

    async def entrypoint(ctx: AgentSession):
        # Initialize game state
        game_state = GameState()
        game_state.player = PlayerStats(
            name="The Witcher",
            health=100,
            max_health=100,
            strength=15,
            agility=14,
            signs=12,
            gold=50,
            inventory=["Steel Sword", "Silver Sword", "2 Swallow Potions", "Witcher Medallion"]
        )
        game_state.current_location = "Crossroads Inn"
        game_state.current_scene = "A stormy night. Rain hammers the roof. Fearful villagers huddle by the fire."

        # Configure LLM
        llm = openai.LLM.with_ollama(
            model="mistral",
            base_url="http://127.0.0.1:11434/v1",
        )

        # Configure TTS - Dramatic male voice for Game Master
        tts = murf.TTS(
            voice="en-UK-hazel",  # British English for fantasy feel
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
            content=GAME_MASTER_INSTRUCTIONS
        )

        # Create agent with all game tools
        agent = Agent(
            instructions=GAME_MASTER_INSTRUCTIONS,
            chat_ctx=initial_ctx,
            llm=llm,
            tts=tts,
            stt=stt,
            vad=vad,
            tools=[
                roll_skill_check,
                update_player_health,
                add_to_inventory,
                remove_from_inventory,
                check_inventory,
                get_player_status,
                update_location,
                record_event,
                add_quest,
                complete_quest,
                meet_npc
            ]
        )

        # Start session with game state
        await ctx.start(
            agent=agent,
            room_input_options=RoomInputOptions(),
            userdata=game_state
        )

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
