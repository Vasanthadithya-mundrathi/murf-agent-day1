# Murf AI Voice Agent - Day 7: Grocery Agent ROBERT 🛒

**Welcome to Day 7 of the Murf AI Voice Agents Challenge!**

Today, I built **ROBERT** - an AI Grocery Shopping Assistant for FreshMart Express that helps customers order groceries via voice!

> **The Core Idea:** A voice-powered quick commerce assistant that takes grocery orders, understands recipe requests, manages a shopping cart, and places orders - all through natural conversation.

## 🤖 Agent Profile

| Agent | Role | Voice |
|-------|------|-------|
| **ROBERT** | Grocery Shopping Assistant | Aarav (Indian English) |

## ✨ Features

-   **Product Catalog**: JSON-based catalog with 30+ grocery items across 8 categories
-   **Smart Cart Management**: Add, remove, update quantities with voice commands
-   **Recipe Intelligence**: Say "I need ingredients for pasta" and it adds all required items
-   **10 Pre-built Recipes**: Peanut butter sandwich, cheese sandwich, pasta, omelette, aloo paratha, poha, fruit salad, breakfast basics, maggi, chai
-   **Order Placement**: Collects name and address, places order with unique ID
-   **Order History**: Check status of previous orders
-   **Delivery Fee Calculation**: Automatic subtotal + delivery fee calculation

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

2.  **Start the Backend Agent (Day 7 Grocery Agent):**
    ```bash
    cd backend
    .venv/bin/python src/grocery_agent.py dev
    ```

3.  **Start the Frontend:**
    ```bash
    cd frontend
    pnpm dev
    ```

4.  Open `http://localhost:3000` and talk to ROBERT, your Grocery Shopping Assistant!

## 📖 How to Use

1. **Connect**: Open the app and click Connect
2. **ROBERT Greets**: ROBERT introduces himself and asks what you'd like to order
3. **Browse or Request**: Ask for specific items or say "I need ingredients for pasta"
4. **Manage Cart**: Add, remove, or update quantities with voice commands
5. **View Cart**: Ask "What's in my cart?" to see items and total
6. **Place Order**: Say "Place my order" and provide your name and address
7. **Order Saved**: Check `backend/shared-data/orders.json` for your order

## 🛒 Sample Products

| Category | Items |
|----------|-------|
| Dairy & Eggs | Milk, Eggs, Butter, Cheese, Curd |
| Bread & Bakery | Whole Wheat Bread, White Bread, Pav Buns |
| Fruits | Apples, Bananas, Oranges |
| Vegetables | Onions, Tomatoes, Potatoes, Capsicum |
| Snacks | Lay's, Kurkure, Parle-G, Aloo Bhujia |
| Beverages | Coca-Cola, Mango Juice, Bisleri Water |
| Pantry | Rice, Atta, Oil, Pasta, Peanut Butter |
| Ready to Eat | Maggi, Poha Mix, Upma Mix |

## 📸 Demo

*(Add your demo video or screenshot here)*

---
*Built with ❤️ by Vasanth for the Murf AI Challenge.*

