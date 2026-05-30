import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DATA_DIR / "tnc_analyzer.db")))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(DATA_DIR / "uploads")))
