from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("URL_SUPABASE"),
    os.getenv("API_SUPABASE")
)

async def store_lesson_text(text: str, author_id: float) -> int:
    """
    Store lesson text in the links table and return the inserted ID
    """
    data = {
        "text": text,
        "author_id": author_id
    }
    result = supabase.table("links").insert(data).execute()
    return result.data[0]["id"] 