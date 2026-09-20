from fastapi import FastAPI

from app.entrypoints.router import router as main_router
from app.domain.core.logger import config_logger


def create_app() -> FastAPI: 
    app = FastAPI()
    
    # Include all routers
    app.include_router(main_router)
    
    # Configure logging
    config_logger()
    
    return app 


app = create_app()
