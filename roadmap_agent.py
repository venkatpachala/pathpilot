import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Initialize the Generative AI model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,  # Adjust temperature for creativity vs. factualness
    convert_system_message_to_human=True, # Recommended for some models and prompt structures
    google_api_key=os.getenv("GOOGLE_API_KEY") # Ensure GOOGLE_API_KEY is set in your .env
)

# Load prompt from a separate file for better organization and easier modification
# Make sure you have a 'prompts' directory with 'roadmap_prompt.txt' inside it
try:
    with open("prompts/roadmap_prompt.txt", "r", encoding="utf-8") as file:
        prompt_template_str = file.read()
except FileNotFoundError:
    print("Error: 'prompts/roadmap_prompt.txt' not found. Please create this file.")
    # Provide a default minimal prompt to allow the app to start, though it won't be as good
    prompt_template_str = """
    You are an expert AI learning assistant. Your task is to create a detailed and actionable learning roadmap.
    The user's goal is: {goal}

    Structure the roadmap with the following sections:
    **1. Foundations/Basics:** Essential prerequisites.
    **2. Core Concepts:** Main building blocks.
    **3. Intermediate Topics:** Deeper understanding.
    **4. Advanced Topics:** Specialized knowledge.
    **5. Tools & Technologies:** Key software and frameworks.
    **6. Projects:** Practical application ideas.
    **7. Career Path & Next Steps:** Guidance for future development.

    For each section, provide specific topics to cover, estimated time, and key resources (e.g., specific courses, books, documentation, tutorials).
    Ensure the roadmap is comprehensive, clear, and easy to follow for a beginner.
    """


# Create a PromptTemplate instance from the loaded string
prompt = PromptTemplate.from_template(prompt_template_str)

def generate_roadmap(goal: str):
    """
    Generates a learning roadmap based on the user's goal using the configured LLM.

    Args:
        goal (str): The learning goal provided by the user.

    Returns:
        str: The generated roadmap content from the LLM.
    """
    # Create a LangChain chain: PromptTemplate -> LLM
    chain = prompt | llm
    
    # Invoke the chain with the user's goal
    response = chain.invoke({"goal": goal})
    
    # Return the content of the AI's response
    return response.content
