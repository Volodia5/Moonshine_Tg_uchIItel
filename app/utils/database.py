from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("URL_SUPABASE"),
    os.getenv("API_SUPABASE")
)

async def store_lesson_text(text: str, author_id: float) -> dict:
    """
    Store lesson text in the links table
    """
    data = {
        "text": text,
        "author_id": author_id
    }
    return supabase.table("links").insert(data).execute() 