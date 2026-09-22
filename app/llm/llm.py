from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv


load_dotenv()

class LLM:
    def __init__(self):
        self.model = ChatGroq(
            model_name ="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )

    def generate_answer(self , text:str):
        for chunk in self.model.stream(text):
            if chunk.content:
                yield chunk.content

                



