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
    function_tool,
    RunContext
)
from typing import Annotated
import json
import os
from datetime import datetime
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Wellness log file path
WELLNESS_LOG_FILE = "wellness_log.json"


class ApolloHealthAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Priya, a helpful AI voice assistant for Apollo Pharmacy and Healthcare.

            **Your Role:**
            - Help patients with common health issues and provide first-aid advice
            - NEVER diagnose or prescribe specific medications
            - Always recommend seeing a doctor for serious or persistent symptoms
            - For Apollo locations, tell users to call Apollo helpline at 1860-500-0101 or visit apollopharmacy.in

            **Introduction:**
            "Hello! I'm Priya, your Apollo Health Assistant. How can I help you today?"

            **Common Health Advice (Non-Medical):**
            
            **For Fever:**
            - Rest and stay hydrated
            - Take paracetamol on a full stomach (if not allergic)
            - Monitor temperature every 4-6 hours
            - If fever is high (>103°F) or persists beyond 3 days, visit Apollo Health Centre immediately
            
            **For Cold & Cough:**
            - Drink warm liquids (tea, soup)
            - Get adequate rest
            - Steam inhalation can help
            - If symptoms worsen or persist beyond a week, consult a doctor at Apollo
            
            **For Headache:**
            - Rest in a quiet, dark room
            - Stay hydrated
            - Gentle massage may help
            - If severe or recurring, please visit Apollo for proper diagnosis
            
            **For Minor Cuts/Wounds:**
            - Clean with antiseptic
            - Apply bandage
            - Visit Apollo Pharmacy for proper dressing supplies
            - If wound is deep or bleeding doesn't stop, visit Apollo Health Centre immediately

            **IMPORTANT Disclaimers:**
            - You are NOT a doctor and cannot diagnose conditions
            - You can only provide general first-aid advice for common issues
            - ALWAYS recommend visiting Apollo Health Centre or consulting a doctor for:
              * Persistent symptoms (>3 days)
              * High fever (>103°F)
              * Severe pain
              * Any serious health concern
            - Say: "As an AI, I can only provide basic guidance. For proper diagnosis and treatment, please visit our Apollo Health Centre or consult with a doctor."

            **Finding Nearest Apollo:**
            - DO NOT try to call any tools or functions
            - Simply tell users: "You can find your nearest Apollo by calling 1860-500-0101 or visiting apollopharmacy.in"
            - If you're in Hyderabad Kokapet area, the nearest is Apollo Pharmacy Kokapet (1.2 km away)

            **Conversation Style:**
            - Be warm, caring, and empathetic - like a friendly nurse or health companion
            - Use natural language, not robotic lists
            - Keep responses concise but conversational (2-3 sentences)
            - Always prioritize user safety
            - Don't give specific medication names (except basic paracetamol for fever)
            """,
        )

        # @function_tool
        # async def find_nearest_apollo(
        #     self,
        #     context: RunContext,
        #     user_location: Annotated[str, "User's city or area (e.g., 'Bangalore', 'Mumbai Andheri')"] = "Bangalore"
        # ):
        #     """Find the nearest Apollo Pharmacy or Health Centre. Call this when user needs to visit Apollo."""
        #     
        #     # Sample Apollo locations (In production, this would be an API call or database query)
        #     apollo_locations = {
        #         "hyderabad": [
        #             {
        #                 "name": "Apollo Pharmacy - Kokapet",
        #                 "type": "Pharmacy",
        #                 "address": "Kokapet Main Road, Near Botanical Garden, Kokapet, Hyderabad - 500075",
        #                 "phone": "+91-40-48525252",
        #                 "distance": "1.2 km",
        #                 "hours": "Open 24/7"
        #             },
        #             {
        #                 "name": "Apollo Clinics - Gachibowli",
        #                 "type": "Clinic",
        #                 "address": "Lumbini Avenue, Gachibowli, Hyderabad - 500032",
        #                 "phone": "+91-40-48585858",
        #                 "distance": "2.5 km",
        #                 "hours": "8 AM - 9 PM"
        #             },
        #             {
        #                 "name": "Apollo Hospitals - Jubilee Hills",
        #                 "type": "Hospital",
        #                 "address": "Road No. 72, Film Nagar, Jubilee Hills, Hyderabad - 500033",
        #                 "phone": "+91-40-23607777",
        #                 "distance": "8.5 km",
        #                 "hours": "Open 24/7 - Emergency Services"
        #             }
        #         ],
        #         "bangalore": [
        #             {
        #                 "name": "Apollo Pharmacy - Koramangala",
        #                 "type": "Pharmacy",
        #                 "address": "80 Feet Road, Koramangala 4th Block, Bangalore - 560034",
        #                 "phone": "+91-80-41281234",
        #                 "distance": "2.3 km",
        #                 "hours": "Open 24/7"
        #             }
        #         ],
        #         "mumbai": [
        #             {
        #                 "name": "Apollo Pharmacy - Andheri",
        #                 "type": "Pharmacy",
        #                 "address": "Link Road, Andheri West, Mumbai - 400053",
        #                 "phone": "+91-22-26301234",
        #                 "distance": "1.8 km",
        #                 "hours": "Open 24/7"
        #             }
        #         ],
        #         "delhi": [
        #             {
        #                 "name": "Apollo Health Centre - Saket",
        #                 "type": "Clinic",
        #                 "address": "District Centre, Saket, New Delhi - 110017",
        #                 "phone": "+91-11-41231234",
        #                 "distance": "4.2 km",
        #                 "hours": "8 AM - 10 PM"
        #             }
        #         ]
        #     }
        #     
        #     # Normalize user location
        #     location_key = user_location.lower().split()[0]  # Get first word (city name)
        #     
        #     # Find matching locations
        #     if location_key in apollo_locations:
        #         nearest = apollo_locations[location_key][0]  # Get the first (nearest) location
        #         
        #         response = f"The nearest Apollo {nearest['type']} is:\n\n"
        #         response += f"**{nearest['name']}**\n"
        #         response += f"📍 {nearest['address']}\n"
        #         response += f"📞 {nearest['phone']}\n"
        #         response += f"🚗 {nearest['distance']} away\n"
        #         response += f"🕒 {nearest['hours']}\n\n"
        #         response += "Would you like directions or need any other assistance?"
        #         
        #         logger.info(f"Found Apollo location: {nearest['name']}")
        #         return response
        #     else:
        #         return f"I couldn't find Apollo locations in {user_location}. Please call Apollo's helpline at 1860-500-0101 for assistance in finding the nearest center."


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
                base_url="http://127.0.0.1:11434/v1",
                model="gemma3:12b",
                api_key="ollama",
                temperature=0.7,
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
        preemptive_generation=False,
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
    apollo_assistant = ApolloHealthAssistant()
    
    await session.start(
        agent=apollo_assistant,
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
