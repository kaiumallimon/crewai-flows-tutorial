from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GENERATIVE_MODEL = os.getenv("GENERATIVE_MODEL")
LLM_PROVIDER = os.getenv("LLM_PROVIDER")

generative_model = ChatGoogleGenerativeAI(
  model = GENERATIVE_MODEL,
  google_api_key = GEMINI_API_KEY,
)