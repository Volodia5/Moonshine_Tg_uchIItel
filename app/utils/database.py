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

async def get_lesson_text(lesson_id: int) -> str:
    """
    Get lesson text from the links table by ID
    """
    result = supabase.table("links").select("text").eq("id", lesson_id).execute()
    if not result.data:
        raise ValueError("Lesson not found")
    return result.data[0]["text"]

async def check_user_exists(user_id: float) -> bool:
    """
    Check if a user exists in the users table
    """
    result = supabase.table("users").select("id").eq("user_id", user_id).execute()
    return len(result.data) > 0

async def save_user(user_id: float, name: str, language: str = "ru") -> int:
    """
    Save a new user to the users table
    """
    data = {
        "user_id": user_id,
        "name": name,
        "language": language
    }
    result = supabase.table("users").insert(data).execute()
    return result.data[0]["id"] 

async def get_user_name(user_id: float) -> str:
    """
    Get user name from the users table by ID
    """
    result = supabase.table("users").select("name").eq("user_id", user_id).execute()
    return result.data[0]["name"] if result.data else None

async def store_quiz_result(user_id: float, link_id: int, correct_answers: int, total_questions: int) -> int:
    """
    Store quiz result in the quiz_results table
    
    Args:
        user_id: Telegram user ID
        link_id: ID of the lesson link
        correct_answers: Number of correct answers
        total_questions: Total number of questions
        
    Returns:
        ID of the inserted record
    """
    # Calculate average score (0-100)
    average_score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    data = {
        "student_id": user_id,
        "link_id": link_id,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "average_score": average_score
    }
    result = supabase.table("quiz_results").insert(data).execute()
    return result.data[0]["id"] if result.data else None

async def get_teacher_links(teacher_id: float):
    """
    Get all links created by a teacher
    
    Args:
        teacher_id: Telegram user ID of the teacher
        
    Returns:
        List of links with their IDs and text
    """
    result = supabase.table("links").select("id, text").eq("author_id", teacher_id).execute()
    return result.data if result.data else []

async def get_quiz_results_by_link(link_id: int):
    """
    Get all quiz results for a specific link
    
    Args:
        link_id: ID of the lesson link
        
    Returns:
        List of quiz results with student names and scores
    """
    result = supabase.table("quiz_results").select("*").eq("link_id", link_id).execute()
    
    # Если есть результаты, получаем имена пользователей
    if result.data:
        # Создаем список для хранения результатов с именами
        results_with_names = []
        
        for quiz_result in result.data:
            # Получаем имя пользователя
            user_result = supabase.table("users").select("name").eq("user_id", quiz_result["student_id"]).execute()
            
            if user_result.data:
                # Добавляем имя к результату
                quiz_result["name"] = user_result.data[0]["name"]
                results_with_names.append(quiz_result)
        
        return results_with_names
    
    return []

async def get_user_language(user_id: float) -> str:
    """
    Get user language from the users table by ID
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Language code (e.g., "ru", "en") or None if user not found
    """
    result = supabase.table("users").select("language").eq("user_id", user_id).execute()
    return result.data[0]["language"] if result.data and "language" in result.data[0] else None

async def set_user_language(user_id: float, language: str) -> bool:
    """
    Set user language in the users table
    
    Args:
        user_id: Telegram user ID
        language: Language code (e.g., "ru", "en")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if user exists
        user_exists = await check_user_exists(user_id)
        
        if user_exists:
            # Update existing user
            result = supabase.table("users").update({"language": language}).eq("user_id", user_id).execute()
            return True
        else:
            # User doesn't exist, can't update language
            return False
    except Exception as e:
        print(f"Error setting user language: {e}")
        return False