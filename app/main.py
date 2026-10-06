from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
import aiohttp

from app.entrypoints.router import router as main_router
from app.domain.core.logger import config_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]: 
    http_client = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=180))
    app.state["http_client"] = http_client
    yield
    await http_client.close()
    

def create_app() -> FastAPI: 
    app = FastAPI(lifespan=lifespan)
    
    # Include all routers
    app.include_router(main_router)
    
    # Configure logging
    config_logger()
    
    return app 


app = create_app()
