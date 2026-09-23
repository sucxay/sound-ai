from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class LLM:
    def __init__(self):
        groq = ChatGroq(
            model = "openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),  
            temperature=0.7
        )
        gemini = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7
        )
        self.model = groq.with_fallbacks([gemini])

        

    def generate_answer(self , text:str):
        for chunk in self.model.stream(text):
            if chunk.content:
                yield chunk.content





