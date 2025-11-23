# Murf AI Voice Agent - Day 2: Starbucks India Barista "Riya" ☕️

**Welcome to Day 2 of the Murf AI Voice Agents Challenge!**

Today, I transformed the agent into **Riya**, a friendly, enthusiastic, and slightly unofficial AI Barista for Starbucks India.

> **Disclaimer:** This is an experimental project and is not officially affiliated with Starbucks. It's built for educational and entertainment purposes.

## 🤖 Agent Profile

-   **Name:** Riya
-   **Role:** AI Barista for Starbucks India
-   **Personality:** Warm, energetic, and passionate about coffee.
-   **Voice:** Murf AI (Natalie - Conversational Style)

## ✨ Features

-   **Smart Ordering:** Takes complex coffee orders including size, milk choice, and extras.
-   **Menu Knowledge:** Knows the full Starbucks India menu (Espresso, Frappuccinos, Cold Brews, etc.).
-   **Conversational Flow:** Handles corrections and maintains a natural dialogue.
-   **Immersive UI:** Custom Starbucks-themed background for the frontend.

## 🛠️ Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground)
-   **Backend:** Python (LiveKit Agents)
-   **Voice (TTS):** **Murf AI** (High-fidelity, human-like speech)
-   **LLM:** **Ollama** (Gemma 3 12B) - *Running Locally for privacy and speed*
-   **STT:** **Deepgram Nova-3** (Fast and accurate transcription)
-   **Real-time Transport:** **LiveKit** (WebRTC infrastructure)

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
    # Using uv (recommended)
    uv sync
    # Or pip
    pip install -r requirements.txt
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

2.  **Start the Backend Agent:**
    ```bash
    cd backend
    source .venv/bin/activate
    python src/agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` in your browser and start chatting with Riya!

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*
