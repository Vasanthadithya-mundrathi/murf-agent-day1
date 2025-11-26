# Murf AI Voice Agent - Day 5: SDR Agent for Razorpay 💼

**Welcome to Day 5 of the Murf AI Voice Agents Challenge!**

Today, I built **Robin** - an AI Sales Development Representative (SDR) for Razorpay that answers FAQs and captures leads.

> **The Core Idea:** A voice-powered SDR that qualifies leads, answers product questions from a knowledge base, and saves lead information for follow-up.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **Robin** | SDR for Razorpay | Natalie (Indian English) |

## ✨ Features

-   **FAQ Knowledge Base**: Answers questions about Razorpay products, pricing, and features
-   **Lead Capture**: Naturally collects lead information during conversation:
    - Name, Company, Email
    - Role/Title
    - Use Case
    - Team Size
    - Timeline (now/soon/later)
-   **Lead Storage**: Saves captured leads to JSON files in `shared-data/leads/`
-   **End-of-Call Summary**: Generates verbal and written summary when call ends
-   **Indian Startup Focus**: Built for Razorpay (India's leading payment gateway)

## 🛠️ Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground)
-   **Backend:** Python (LiveKit Agents with Function Tools)
-   **Voice (TTS):** **Murf AI Falcon** - Natalie (Indian English)
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

2.  **Start the Backend Agent (Day 5 SDR):**
    ```bash
    cd backend
    .venv/bin/python src/sdr_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and talk to Robin, your SDR!

## 📖 How to Use

1. **Connect**: Open the app and click Connect
2. **Chat**: Robin greets you and asks what brought you here
3. **Ask Questions**: Ask about Razorpay products, pricing, integrations
4. **Share Info**: Naturally share your details during conversation
5. **End Call**: Say "Thanks, that's all" to get a summary
6. **Check Leads**: Find captured lead data in `backend/shared-data/leads/`

## 📝 Sample Questions to Ask

- "What does Razorpay do?"
- "What payment methods do you support?"
- "Do you have a free tier?"
- "How long does integration take?"
- "Is it secure?"

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*
