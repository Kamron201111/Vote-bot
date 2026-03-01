import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
TOKEN_ADMIN = os.getenv("TOKEN_ADMIN")
PASSWORD = os.getenv("PASSWORD")
VOTE_URL = os.getenv("VOTE_URL", "https://example.com/vote")

if not TOKEN:
    raise ValueError("❌ TOKEN topilmadi! .env faylini tekshiring")
if not TOKEN_ADMIN:
    raise ValueError("❌ TOKEN_ADMIN topilmadi! .env faylini tekshiring")
if not PASSWORD:
    raise ValueError("❌ PASSWORD topilmadi! .env faylini tekshiring")
