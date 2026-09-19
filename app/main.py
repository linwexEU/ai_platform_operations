from fastapi import FastAPI

from app.entrypoints.router import router as main_router


def create_app() -> FastAPI: 
    app = FastAPI()
    
    # Include all routers
    app.include_router(main_router)
    
    return app 


app = create_app()
