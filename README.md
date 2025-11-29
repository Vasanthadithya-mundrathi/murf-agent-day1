# Murf AI Voice Agent - Day 8: Game Master Agent 🎲⚔️

**Welcome to Day 8 of the Murf AI Voice Agents Challenge!**

Today, I built a **Voice Game Master** - A D&D-style adventure narrator set in The Witcher universe!

> **The Core Idea:** A voice-powered Game Master that runs an interactive adventure, tracks player stats, performs dice rolls, and guides you through a dark fantasy story - all through voice conversation.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **Game Master** | D&D-Style Narrator | Hazel (British English) |

## ✨ Features

-   **The Witcher Universe**: Dark fantasy setting with monster hunting, moral choices, and magic
-   **Dice Roll Mechanics**: D20 skill checks for risky actions (strength, agility, signs/magic)
-   **Player Character Sheet**: Track health, stats, inventory, and gold
-   **Dynamic Story Arc**: Beginning → Rising → Climax → Resolution pacing
-   **NPC Tracking**: Remember characters you've met and their attitudes
-   **Quest System**: Active quests, completion tracking, and gold rewards
-   **Location System**: Track your journey through the world
-   **Event History**: The GM remembers all your past decisions


## 🛠️ Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground)
-   **Backend:** Python (LiveKit Agents with Function Tools)
-   **Voice (TTS):** **Murf AI Falcon** - Arjun (Indian English)
-   **LLM:** **Ollama** (Mistral 7B) - *Running Locally*
-   **STT:** **Deepgram Nova-3**
-   **Real-time Transport:** **LiveKit** (WebRTC)

## 🚀 Setup & Run

### Prerequisites
-   Python 3.11+
-   Node.js 18+ & pnpm
-   Docker (for LiveKit Server)
-   Ollama (running `mistral:latest`)

### Installation

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/Vasanthadithya-mundrathi/murf-agent-day1.git
    cd murf-agent-day1
    ```

2.  **Install Backend Dependencies:**
    ```bash
    cd backend
    uv sync
    ```

3.  **Install Frontend Dependencies:**
    ```bash
    cd frontend
    pnpm install
    ```

4.  **Environment Configuration:**
    Create a `.env.local` file in `backend/` with your API keys:
    ```env
    LIVEKIT_URL=ws://127.0.0.1:7880
    LIVEKIT_API_KEY=devkey
    LIVEKIT_API_SECRET=secret
    MURF_API_KEY=your_murf_api_key
    DEEPGRAM_API_KEY=your_deepgram_api_key
    ```

### Running the Application

1.  **Start LiveKit Server:**
    ```bash
    docker-compose up
    ```

2.  **Start the Backend Agent (Day 8 Game Master):**
    ```bash
    cd backend
    .venv/bin/python src/game_master_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and begin your Witcher adventure!

## 📖 How to Play

1. **Connect**: Open the app and click Connect
2. **GM Sets the Scene**: The Game Master describes the stormy Crossroads Inn
3. **Explore**: Say what you want to do ("I approach the innkeeper", "I look around")
4. **Take Quests**: NPCs will offer you monster contracts
5. **Investigate**: Gather clues about the mysterious disappearances
6. **Combat**: When you fight, the GM rolls dice for your actions
7. **Make Choices**: Your decisions shape the story's outcome

## 🎮 Game Mechanics

| Mechanic | Description |
|----------|-------------|
| **Skill Checks** | D20 + modifier vs difficulty class |
| **Health** | 100 HP max, status changes at thresholds |
| **Stats** | Strength, Agility, Signs (magic) |
| **Inventory** | Steel Sword, Silver Sword, Swallow Potions |
| **Story Arc** | 4 phases over ~12 turns |

## 🗡️ Starting Equipment

- Steel Sword (for humans)
- Silver Sword (for monsters)
- 2 Swallow Potions (healing)
- Witcher Medallion
- 50 Gold Crowns

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*

