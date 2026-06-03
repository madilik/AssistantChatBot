import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ВНИМАНИЕ: API ключ GEMINI_API_KEY не найден в файле .env!")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def get_embedding(text):
    """
    Превращает входной текст в математический вектор размерностью 768.
    Использует актуальную библиотеку google-genai.
    """
    if not text or not text.strip() or not client:
        return None

    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Ошибка при получении эмбеддинга: {e}")
        return None


def generate_llm_response(system_prompt, user_query):
    """
    Генерация ответа с использованием новейшей модели Gemini 2.5 Flash
    """
    if not client:
        return "Ошибка настройки: API ключ Gemini не найден."

    try:
        full_prompt = f"{system_prompt}\nВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}\nОТВЕТ:"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        print(f"Ошибка генерации ответа LLM: {e}")
        return "Извините, в данный момент интеллектуальная система недоступна. Пожалуйста, обратитесь к оператору Технопарка."