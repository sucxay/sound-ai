from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv


load_dotenv()

class LLM:
    def __init__(self):
        self.model = ChatGroq(
            model_name ="Llama 3.1 8B ",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )

    def generate_answer(self,question:str)-> str:
        text = self.model.invoke(question)

        return text.content



