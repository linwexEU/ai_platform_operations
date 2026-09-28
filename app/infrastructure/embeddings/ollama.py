import asyncio
from json import JSONDecodeError
import logging

import aiohttp

from app.domain.core.config import settings

logger = logging.getLogger()


async def generate_embedding(session: aiohttp.ClientSession, input_: str) -> list[float]: 
    try:
        async with session.post(
            "http://localhost:11434/api/embed", 
            headers={"Content-Type": "application/json"}, 
            json={
                "model": settings.OLLAMA_EMBEDDING_MODEL, 
                "input": input_
            }
        ) as response: 
            response.raise_for_status()
            payload = await response.json() 
            return payload["embeddings"][0]
    except aiohttp.ClientConnectorError as err: 
        logger.error(f"Ollama: {settings.OLLAMA_EMBEDDING_MODEL} is down: {str(err)}")
        raise
    except aiohttp.ServerTimeoutError as err: 
        logger.error(f"Ollama timeout: {str(err)}")
        raise
    except aiohttp.ClientResponseError as err: 
        logger.error(f"Ollama client response error: {str(err)}")
        raise
    except aiohttp.ClientPayloadError: 
        logger.error(f"Ollama client payload error: {response.status}")
        raise
    except (aiohttp.ContentTypeError, JSONDecodeError):
        logger.error(f"Ollama invalid response: {response.status}")
        raise
    except (KeyError, IndexError): 
        logger.error(f"Ollama invalid json response: {payload}")
        raise


async def generate_embeddings(session: aiohttp.ClientSession, inputs: list[str]) -> list[list[float]]: 
    tasks = [
        asyncio.create_task(generate_embedding(session, input_)) 
        for input_ in inputs
    ]
    embeddings = await asyncio.gather(*tasks)
    return embeddings
