# Murf AI Voice Agent - Day 1: Cybersecurity Agent "Ruby"

This project is part of the **Murf AI Voice Agents Challenge (Day 1)**.

**Agent Name:** Ruby
**Persona:** Cybersecurity Expert & Virtual Penetration Tester
**Creator:** Vasanth

## Demo Video

https://github.com/user-attachments/assets/placeholder-for-video-upload
*(Note: Please upload `aiagentday1.mov` to the GitHub release or issue to get a link, or commit it to the repo if size permits. For now, it is in the root directory: `aiagentday1.mov`)*

## Tech Stack

-   **Frontend:** Next.js / React (LiveKit Agent Playground)
-   **Backend:** Python (LiveKit Agents)
-   **Voice:** Murf Falcon TTS (Ultra-fast, high quality)
-   **LLM:** Ollama (Gemma 3 12B) - *Running Locally*
-   **STT:** Deepgram Nova-3
-   **Real-time Transport:** LiveKit

## Features

-   **Conversational Security Advice:** Ruby explains complex security concepts simply.
-   **Penetration Testing Simulation:** Can walk through hypothetical pentest scenarios.
-   **Local Privacy:** Uses a local LLM (Ollama) for intelligence.
-   **Ultra-Low Latency:** Powered by Murf Falcon and LiveKit.

## Setup & Run

1.  **Prerequisites:**
    -   Python 3.11+
    -   Node.js 18+ & pnpm
    -   Ollama (running `gemma3:12b`)
    -   LiveKit Server (local or cloud)

2.  **Install Dependencies:**
    ```bash
    # Backend
    cd backend
    uv sync
    
    # Frontend
    cd frontend
    pnpm install
    ```

3.  **Configure Environment:**
    -   Copy `.env.example` to `.env.local` in both `backend/` and `frontend/`.
    -   Add your API keys (LiveKit, Murf, Deepgram).

4.  **Run:**
    ```bash
    ./start_app.sh
    ```

## Original Documentation

For the original challenge instructions and details, see [murfinfo.md](./murfinfo.md).
