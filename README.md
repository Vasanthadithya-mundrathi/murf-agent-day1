# Murf AI Voice Agent - Day 6: Fraud Alert Agent LEO 🔒

**Welcome to Day 6 of the Murf AI Voice Agents Challenge!**

Today, I built **LEO** - an AI Fraud Detection Agent for SecureBank India that verifies suspicious transactions with customers.

> **The Core Idea:** A voice-powered fraud detection system that calls customers about suspicious transactions, verifies their identity, and takes immediate action to protect their accounts.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **LEO** | Fraud Detection Agent | Arjun (Indian English) |

## ✨ Features

-   **Fraud Case Database**: JSON-based database with 5 sample fraud cases
-   **Identity Verification**: Secure verification using security questions (no sensitive data)
-   **Transaction Details**: Reads out suspicious transaction info (amount, merchant, location, time)
-   **Three Outcomes**:
    - ✅ `confirmed_safe` - Customer confirms they made the transaction
    - 🚨 `confirmed_fraud` - Customer denies, card blocked, dispute raised
    - ❌ `verification_failed` - Cannot verify identity, manual review required
-   **Database Updates**: Persists case status and outcome notes back to JSON

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

2.  **Start the Backend Agent (Day 6 Fraud Agent):**
    ```bash
    cd backend
    .venv/bin/python src/fraud_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and talk to LEO, your Fraud Detection Agent!

## 📖 How to Use

1. **Connect**: Open the app and click Connect
2. **LEO Greets**: LEO introduces himself as SecureBank's fraud detection agent
3. **Provide Username**: Give a test username (rahul, priya, amit, neha, or vikram)
4. **Answer Security Question**: LEO asks your security question for verification
5. **Review Transaction**: LEO reads the suspicious transaction details
6. **Confirm or Deny**: Say "yes" if you made it, "no" if it's fraud
7. **Case Updated**: Check `backend/shared-data/fraud_cases.json` for updated status

## 📝 Test Usernames

| Username | Card | Amount | Merchant |
|----------|------|--------|----------|
| rahul | *4521 | ₹45,999 | TechGadgets Pro |
| priya | *8834 | ₹12,500 | LuxuryWatches Ltd |
| amit | *2267 | ₹78,450 | CryptoExchange Global |
| neha | *6109 | ₹3,299 | StreamFlix Premium |
| vikram | *3345 | ₹1,25,000 | ElectroMart International |

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*
