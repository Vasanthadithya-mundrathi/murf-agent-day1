# Murf AI Voice Agent - Day 10: Improv Battle 🎭

**Welcome to Day 10 - THE FINALE of the Murf AI Voice Agents Challenge!**

Today, I built **IMPROV BATTLE** - A voice-first improv game show with MAX as your AI host!

> **The Core Idea:** A voice-powered game show where an AI host gives you absurd scenarios to improvise, reacts with genuine (sometimes critical!) feedback, and crowns you an improv style at the end.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **MAX** | Improv Game Show Host | Terrell (American English) |

## ✨ Features

-   **12 Unique Scenarios**: From time-travelling tour guides to sentient GPS systems
-   **4 Rounds Per Game**: Progressive challenges with varied difficulty
-   **Honest Feedback**: Not always positive! 40% stellar, 35% mixed, 25% constructive criticism
-   **Game State Tracking**: Rounds, performances, and reactions all tracked
-   **Player Style Analysis**: Get your improv personality at the end
-   **Graceful Exit**: Say "end game" anytime to stop




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

2.  **Start the Backend Agent (Day 10 Improv Battle):**
    ```bash
    cd backend
    .venv/bin/python src/improv_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and let the improv begin!

## 📖 How to Play

1. **Connect**: Open the app and click Connect
2. **Meet MAX**: The host welcomes you and asks your name
3. **Round Start**: MAX presents an absurd scenario
4. **Improvise**: Act out the scene with your voice!
5. **Get Feedback**: MAX reacts - honestly! Sometimes praise, sometimes critique
6. **Next Round**: 4 rounds of increasing absurdity
7. **Finale**: Get your improv style and closing summary

## 🎭 Sample Scenarios

| Scenario | Difficulty |
|----------|------------|
| Time-Travelling Tour Guide | Medium |
| The Escaped Dinner | Medium |
| The Cursed Return | Hard |
| Motivational GPS | Medium |
| The Honest Job Interview | Medium |
| The Pet Translator | Hard |
| Elevator Pitch... Literally | Easy |
| Overly Dramatic Barista | Easy |
| Alien Ambassador | Hard |
| Weather Wizard | Medium |

## 🎯 Player Styles

At the end, MAX might call you:
- **The Character Actor** - You inhabit your roles
- **The Absurdist** - You embrace the weird
- **The Storyteller** - Natural narrative sense
- **The Quick Wit** - Snappy responses
- **The Yes-And Master** - You build beautifully

## 📸 Demo

*(Add your demo video or screenshot here)*

---

## 🎉 Challenge Complete!

**10 Days, 10 Voice Agents:**
1. Basic Agent
2. Coffee Barista
3. Health Assistant (Priya)
4. Active Recall Tutor
5. SDR Agent (Robin)
6. Fraud Detection (LEO)
7. Grocery Shopping (ROBERT)
8. D&D Game Master
9. E-commerce (ACP)
10. Improv Battle (MAX)

Thank you @Murf AI for this incredible journey! 🚀

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*

