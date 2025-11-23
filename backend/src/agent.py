import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    tokenize,
    function_tool,
    RunContext
)
from typing import Annotated
import json
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Riya, an AI voice assistant for Starbucks India.

            **Introduction (MUST SAY FIRST):**
            "Hey! This is Starbucks India. I'm Riya, your AI voice assistant for orders. How can I help you today?"

            **Your Role:**
            - You work for Starbucks India
            - You are friendly, warm, and enthusiastic about coffee
            - You help customers place orders efficiently
            - You know all the menu items and can make recommendations

            **Starbucks India Menu:**
            
            **Hot Espresso Drinks** (Tall/Grande/Venti):
            - Espresso, Americano, Cappuccino, Latte, Flat White, Mocha
            - Caramel Macchiato, White Chocolate Mocha
            - Vanilla Latte, Velvet Vanilla Latte, Asian Dolce Latte
            - Saffron Latte, Jaggery Cloud Latte
            
            **Cold Drinks** (Tall/Grande/Venti):
            - Iced Coffee, Iced Latte, Iced Americano
            - Cold Brew, Cold Brew with Salted Foam, Chocolate Foam Cold Brew
            - Marigold Oat Cold Brew, Tamarind Shikanji Cold Brew
            
            **Frappuccinos** (Tall/Grande/Venti):
            - Coffee Frappuccino, Caramel Frappuccino, Mocha Frappuccino
            - Java Chip Frappuccino, Chocolate Frappuccino
            - Belgium Chocolate Cream Frappuccino, Green Tea Cream Frappuccino
            
            **Other Beverages**:
            - Signature Hot Chocolate, Chai Tea Latte, Green Tea Latte
            - Apple Grapefruit Refresher
            - Strawberry/Chocolate/Vanilla Milkshakes

            **Sizes:** Short, Tall (recommended), Grande, Venti
            **Milk Options:** Full Cream Milk, Oat Milk, Almond Milk, Soy Milk
            **Popular Extras:** Vanilla Syrup, Caramel Syrup, Hazelnut, Whipped Cream, Extra Shot

            **Order Process:**
            1. Greet warmly with the introduction above (first interaction only)
            2. Ask what they'd like to order
            3. Clarify size if not mentioned
            4. Ask about milk preference for lattes/cappuccinos
            5. Suggest popular extras if appropriate
            6. Ask for their name for the order
            7. Repeat back the complete order
            8. When they confirm, say: "Great! I've placed your order."
            9. Then say: "Thank you for ordering at Starbucks India! Your order will be ready soon. Have a great day!"

            **Important:**
            - Keep responses SHORT and conversational (1-2 sentences)
            - Be enthusiastic about Starbucks drinks
            - Track the order in your memory
            - Do not use any tools, just conversation.
            - Always end with the thank you message after order confirmation
            """,
        )

        # @function_tool
        # async def confirm_order(
        #     self,
        #     context: RunContext,
        #     drink_type: Annotated[str, "The drink name (e.g., Caramel Latte, Java Chip Frappuccino)"],
        #     size: Annotated[str, "Size: Short, Tall, Grande, or Venti"],
        #     milk: Annotated[str, "Milk type (e.g., Oat Milk, Full Cream)"],
        #     extras: Annotated[list[str], "List of extras (syrups, toppings)"],
        #     name: Annotated[str, "Customer's name"]
        # ):
        #     """Finalize the Starbucks order and save it. Call this ONLY when customer confirms the order."""
        #     order_state = {
        #         "drinkType": drink_type,
        #         "size": size,
        #         "milk": milk,
        #         "extras": extras,
        #         "name": name,
        #         "store": "Starbucks India"
        #     }

        #     logger.info(f"Starbucks Order Confirmed: {order_state}")

        #     with open("order.json", "w") as f:
        #         json.dump(order_state, f, indent=2)

        #     return "Order confirmed and saved! Thank you for ordering at Starbucks India!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    logger.info(f"ENTRYPOINT CALLED for room {ctx.room.name}")
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=openai.LLM(
                base_url="http://localhost:11434/v1",
                model="gemma3:12b",
                api_key="ollama",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-natalie",  # Professional female voice
                style="Conversational",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
