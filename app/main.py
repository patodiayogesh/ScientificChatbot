import logging
import sys
import uvicorn

from fastapi import FastAPI
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level (e.g., DEBUG, INFO, WARNING, ERROR)
    format="%(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.StreamHandler()  # Output logs to the terminal
    ]
)

logger = logging.getLogger(__name__)
app = FastAPI(
    title = "Scientific Chatbot",
    summary = "An AI-powered chatbot for scientific queries",
)
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")