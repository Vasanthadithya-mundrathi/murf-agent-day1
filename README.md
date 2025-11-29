# Murf AI Voice Agent - Day 9: E-commerce Agent 🛍️

**Welcome to Day 9 of the Murf AI Voice Agents Challenge!**

Today, I built an **ACP-Inspired E-commerce Voice Agent** for TechStyle Store - a developer merchandise shop!

> **The Core Idea:** A voice-powered shopping assistant following Agentic Commerce Protocol patterns - browse products, manage cart, and place orders through natural conversation.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **Shop Assistant** | E-commerce Agent | Natalie (American English) |

## ✨ Features

-   **15 Developer Products**: Mugs, t-shirts, hoodies, stickers, caps, and accessories
-   **Smart Filtering**: Browse by category, price range, or color
-   **Cart Management**: Add, remove, update quantities with voice
-   **Size Selection**: Automatic prompts for clothing sizes (S, M, L, XL)
-   **ACP-Style Orders**: Structured order objects with line items, buyer info, and status
-   **Order History**: View past orders and total spending
-   **Reference Tracking**: "Add the first one" works after browsing



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

2.  **Start the Backend Agent (Day 9 E-commerce Agent):**
    ```bash
    cd backend
    .venv/bin/python src/ecommerce_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and start shopping!

## 📖 How to Shop

1. **Connect**: Open the app and click Connect
2. **Browse**: "Show me hoodies" or "What mugs do you have under 500?"
3. **Details**: "Tell me more about the Code Ninja Hoodie"
4. **Add to Cart**: "Add that hoodie in size L" or "I'll take the first one"
5. **Review**: "What's in my cart?"
6. **Checkout**: "Place my order, my name is Rahul"
7. **Confirm**: Order saved to `backend/shared-data/ecommerce_orders.json`

## 🛒 Product Categories

| Category | Products | Price Range |
|----------|----------|-------------|
| Mugs | Developer, Python, Debug | ₹399 - ₹699 |
| T-Shirts | Git, React, AI/ML | ₹799 - ₹999 |
| Hoodies | Code Ninja, Open Source, Dark Mode | ₹1,999 - ₹2,499 |
| Stickers | Developer Pack, Framework Pack | ₹199 - ₹299 |
| Caps | Binary Code, AWS | ₹599 - ₹699 |
| Accessories | RGB Mousepad, Minimal Mousepad | ₹499 - ₹1,299 |

## 📦 ACP-Style Order Structure

```json
{
  "id": "ORD-ABC12345",
  "status": "CONFIRMED",
  "buyer": { "name": "...", "email": "..." },
  "line_items": [
    { "product_id": "...", "quantity": 1, "unit_amount": 999, "size": "L" }
  ],
  "total": { "amount": 999, "currency": "INR" }
}
```

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*

