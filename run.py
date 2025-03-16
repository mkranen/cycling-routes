import uvicorn

from backend.logging_config import configure_logging

if __name__ == "__main__":
    # Configure logging
    logger = configure_logging()
    logger.info("Starting FastAPI application with INFO logging level")

    # Run the FastAPI application
    uvicorn.run(
        "backend.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
