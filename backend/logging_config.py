import logging


def configure_logging():
    """
    Configure logging for the application.
    Sets the root logger level to INFO and configures formatters.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set specific loggers to INFO level
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    # logging.getLogger("sqlalchemy").setLevel(logging.INFO)

    # You can add more specific logger configurations here

    # Return the root logger for convenience
    return logging.getLogger()
