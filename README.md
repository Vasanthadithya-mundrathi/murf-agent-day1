# Murf AI Voice Agent - Day 4: Active Recall Coach 📚

**Welcome to Day 4 of the Murf AI Voice Agents Challenge!**

Today, I built **Teach-the-Tutor** - an Active Recall Coach that helps you learn programming concepts through three different learning modes with agent handoffs.

> **The Core Idea:** The best way to learn is to teach! The agent explains topics, quizzes you, then asks YOU to explain them back.

## 🤖 Agent Profiles

This system features **four specialized agents** with different Murf voices:

| Agent | Role | Voice |
|-------|------|-------|
| **Coordinator** | Greets users, explains modes, handles mode selection | Matthew |
| **Learn Mode** | Explains programming concepts clearly | Matthew |
| **Quiz Mode** | Tests knowledge with questions | Alicia |
| **Teach-Back Mode** | Listens to your explanations, gives feedback | Ken |

## ✨ Features

-   **Three Learning Modes:**
    -   **Learn**: Get clear explanations of programming concepts
    -   **Quiz**: Answer questions and get feedback
    -   **Teach-Back**: Explain concepts back and receive constructive feedback
-   **Agent Handoffs**: Seamlessly switch between modes at any time
-   **Content-Driven**: All concepts loaded from `shared-data/day4_tutor_content.json`
-   **Five Programming Concepts**: Variables, Loops, Functions, Conditionals, Data Types

## 🛠️ Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground)
-   **Backend:** Python (LiveKit Agents with Agent Handoffs)
-   **Voice (TTS):** **Murf AI Falcon** - 3 different voices (Matthew, Alicia, Ken)
-   **LLM:** **Ollama** (Gemma 3 12B) - *Running Locally*
-   **STT:** **Deepgram Nova-3**
-   **Real-time Transport:** **LiveKit** (WebRTC)

## 🚀 Setup & Run

### Prerequisites
-   Python 3.11+
-   Node.js 18+ & pnpm
-   Docker (for LiveKit Server)
-   Ollama (running `gemma3:12b`)

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

2.  **Start the Backend Agent (Day 4 Tutor):**
    ```bash
    cd backend
    .venv/bin/python src/tutor_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and start learning with the Active Recall Coach!

## 📖 How to Use

1. **Start**: The Coordinator welcomes you and explains the three modes
2. **Choose a Mode**: Say "I want to learn" or "quiz me" or "teach back"
3. **Learn**: Get explanations of Variables, Loops, Functions, etc.
4. **Quiz**: Answer questions and receive feedback
5. **Teach-Back**: Explain concepts in your own words
6. **Switch Anytime**: Just say "switch to quiz mode" or "let me learn"

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*
