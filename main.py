from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext

from livekit.plugins import (
    openai,
    google,
    silero,
    noise_cancellation,
)
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email
import os
from livekit.plugins import tavus

from mem0 import AsyncMemoryClient
import json
import logging




load_dotenv()


class Assistant(Agent):
    def __init__(self,cht_ctx=None) -> None:
        super().__init__(
        instructions="You are a helpful voice AI assistant.",
        llm = openai.LLM(
            model=os.getenv("OPENAI_MODEL_ID"),
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        stt=google.STT(),
        tts=google.TTS(),
        
        
        tools=[get_weather,search_web,send_email],
        chat_ctx=cht_ctx
    )



async def entrypoint(ctx: agents.JobContext):
    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        logging.info("Shutting down, saving chat context to memory...")

        messages_formatted = [
        ]

        logging.info(f"Chat context messages: {chat_ctx.items}")

        for item in chat_ctx.items:
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)

            if memory_str and memory_str in content_str:
                continue

            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })

        logging.info(f"Formatted messages to add to memory: {messages_formatted}")
        await mem0.add(messages_formatted, user_id="guru")
        logging.info("Chat context saved to memory.")
    session = AgentSession(
    
    )
    
    mem0 = AsyncMemoryClient()
    user_name = "guru"
    results = await mem0.get_all(user_id=user_name)
    initial_ctx = ChatContext()
    memory_str=""
    if results:
        memories = [
            {
                "memory": result["memory"],
                "updated_at": result["updated_at"]
            }
            for result in results
        ]
        memory_str = json.dumps(memories)
        logging.info(f"Memories: {memory_str}")
        initial_ctx.add_message(
            role="assistant",
            content=f"The user's name is {user_name}, and this is relvant context about him: {memory_str}."
        )

    
    # avatar = tavus.AvatarSession(
    #   replica_id=os.environ.get("REPLICA_ID"),  
    #   persona_id=os.environ.get("PERSONA_ID"),  
    #   api_key=os.environ.get("TAVUS_API_KEY"),
    # )

    # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)
    

    await session.start(
        room=ctx.room,
        agent=Assistant(cht_ctx=initial_ctx),
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` instead for best results
            video_enabled=True,
            
            noise_cancellation=noise_cancellation.BVC(),
            
        ),
    )
    await ctx.connect()
    # await speak_with_avatar(session, "Hello, I am your AI avatar. How can I help you today?")
    

    # Start the avatar and wait for it to join
    

    
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )
    ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_str))


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))