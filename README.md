# Murf AI Voice Agent - Day 3: Apollo Health Assistant "Priya" 🏥

**Welcome to Day 3 of the Murf AI Voice Agents Challenge!**

Today, I shifted gears from coffee to care. I transformed the agent into **Priya**, a warm, empathetic, and helpful AI Health Assistant for Apollo Pharmacy/Healthcare.

> **Disclaimer:** This is an experimental project and is not officially affiliated with Apollo Hospitals. **Priya is an AI, not a doctor.** Always consult a professional for medical advice.

## 🤖 Agent Profile

-   **Name:** Priya
-   **Role:** AI Health Assistant for Apollo Pharmacy
-   **Personality:** Caring, empathetic, professional, and reassuring. Like a friendly nurse or health companion.
-   **Voice:** Murf AI (Natalie - Conversational Style)

## ✨ Features

-   **First-Aid Advice:** Provides immediate, non-medical guidance for common issues like fever, cold, cough, headache, and minor cuts.
-   **Location Awareness:** Specifically tuned for **Hyderabad (Kokapet)** area, guiding users to the nearest Apollo Pharmacy (1.2 km away).
-   **Safety First:** Strictly programmed to NEVER diagnose or prescribe. Always recommends visiting a doctor for serious or persistent symptoms.
-   **Immersive UI:** Complete frontend transformation with a soothing **Apollo Blue** animated gradient theme and medical aesthetics.

## 🛠️ Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground) - *Custom Apollo Theme*
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

4.  Open `http://localhost:3000` in your browser and start chatting with Priya!

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*
