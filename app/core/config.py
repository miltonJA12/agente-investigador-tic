import os
from pathlib import Path
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]

load_dotenv(RAIZ / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")