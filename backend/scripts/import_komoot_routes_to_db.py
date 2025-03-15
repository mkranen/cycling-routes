import logging
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from database import engine
from models.models import KomootRoute, Route
from sqlmodel import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    sources = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else ["personal", "gravelritten", "gijs_bruinsma"]
    )

    with Session(engine) as session:
        KomootRoute.download_and_import(session, sources)
