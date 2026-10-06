import asyncio
import json
from typing import AsyncGenerator

from aiohttp import ClientSession

from app.domain.core.config import settings


async def stream_llm_response(history: list[str], http_client: ClientSession) -> AsyncGenerator[str]: 
    try:
        async with http_client.post(
            "http://localhost:11434/api/chat", 
            json={"model": settings.OLLAMA_CHAT_MODEL, "messages": history, "stream": True}
        ) as response: 
            response.raise_for_status()
            async for line in response.content: 
                if not line.strip(): 
                    continue
                payload = json.loads(line)
                if payload.get("done"): 
                    break
                delta = payload["message"]["content"]
                yield delta
    except asyncio.CancelledError: 
        pass
