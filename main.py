"""Main entry point for Kingdom Wars Bot."""
import uvicorn
from config.settings import settings


def main():
    """Start the Kingdom Wars Bot server."""
    uvicorn.run(
        "src.server:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
