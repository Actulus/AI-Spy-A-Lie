import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os
from sockets import socketio_app
from endpoints import router as highscore_router
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditionally include OpenAPI based on CONFIG_MODE
config_mode = os.getenv('CONFIG_MODE')

open_api_url = ""

if config_mode == 'development':
    open_api_url = '/openapi.json'

# Initialize FastAPI app
app = FastAPI(openapi_url=open_api_url)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI-Spy-A-Lie API",
        version="1.0.0",
        description="API for AI-Spy-A-Lie game",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set custom OpenAPI schema
app.openapi = custom_openapi


app.mount('/sockets', app=socketio_app)
app.include_router(highscore_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def home():
    return {'message': 'Hello👋 Developers💻'}

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)