import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMManager:
    def __init__(self):
        # ollama / gemini / openai
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    def get_llm(self):
        # ---------- GEMINI ----------
        if self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            return ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
                temperature=0,
                google_api_key=api_key
            )

        # ---------- OPENAI ----------
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")

            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=api_key
            )

        # ---------- OLLAMA (fallback) ----------
        else:
            model_name = os.getenv("OLLAMA_MODEL", "phi3:mini")
            return ChatOllama(
                model=model_name,
                temperature=0
            )