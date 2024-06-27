from fastapi import Depends, FastAPI

from .logging_config import LogConfig
from .routes import chatbot_route, monitor_route, endpoint_route, endpoint_ws_route
from fastapi.middleware.cors import CORSMiddleware


logger = LogConfig("main").get_logger()

app = FastAPI()

# Add CORS middleware with timeout
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://chat-gpt-frontend-2023.s3-website-ap-southeast-2.amazonaws.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"],
    max_age=240,  # Timeout value in seconds
)

app.include_router(chatbot_route.router)
app.include_router(monitor_route.router)
app.include_router(endpoint_route.router)
app.include_router(endpoint_ws_route.router)

logger.info("Server started!")

