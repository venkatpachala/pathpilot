from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    convert_system_message_to_human=True,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Load prompt from file
with open("prompts/roadmap_prompt.txt", "r", encoding="utf-8") as file:
    prompt_template_str = file.read()

prompt = PromptTemplate.from_template(prompt_template_str)

def generate_roadmap(goal: str):
    chain = prompt | llm
    response = chain.invoke({"goal": goal})
    return response.content
