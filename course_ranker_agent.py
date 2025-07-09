import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict

load_dotenv()

# Define the Pydantic model for the output structure
class RankedCourse(BaseModel):
    title: str = Field(description="Title of the course.")
    link: str = Field(description="Direct URL link to the course.")
    reason: str = Field(description="A brief reason why this course is recommended for the user's goal and topic, especially for beginners in India.")

class RankedCoursesList(BaseModel):
    ranked_courses: List[RankedCourse] = Field(description="A list of ranked courses, from most to least recommended.")

llm_ranker = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.4, # Lower temperature for more factual and less creative ranking
    # convert_system_message_to_human=True, # Deprecated and removed
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Set up the parser for structured output
parser = JsonOutputParser(pydantic_object=RankedCoursesList)

# Define the prompt for the course ranker
ranker_prompt_template = """
You are an AI assistant specialized in recommending online courses.
Your task is to review a list of online courses for a user's specific learning goal and a particular topic within that goal.
The user's overall goal is: {user_goal}
The current specific topic they are looking for courses on is: {current_topic}

Here is a list of courses found:
{courses_list}

Please rank these courses from most recommended to least recommended for a complete beginner in India, specifically considering their overall learning goal and the current topic.
Provide a brief reason for each recommendation. Prioritize courses that seem comprehensive, beginner-friendly, and relevant.

Return the response as a JSON object with a single key 'ranked_courses' which is a list of objects.
Each object in the 'ranked_courses' list should have 'title', 'link', and 'reason' keys.
The 'reason' should explain why it's suitable, especially for a beginner in India.
Do NOT include any additional text outside the JSON.

{format_instructions}
"""

ranker_prompt = PromptTemplate(
    template=ranker_prompt_template,
    input_variables=["user_goal", "current_topic", "courses_list"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def rank_courses(user_goal: str, current_topic: str, courses: List[Dict]) -> List[Dict]:
    """
    Ranks a list of courses based on user goal and current topic using Gemini.

    Args:
        user_goal (str): The user's overall learning goal.
        current_topic (str): The specific topic for which courses are being searched.
        courses (List[Dict]): A list of course dictionaries, each containing 'title', 'link', and 'snippet'.

    Returns:
        List[Dict]: A list of ranked course dictionaries, including 'title', 'link', and 'reason'.
                    Returns an empty list if ranking fails.
    """
    if not courses:
        return []

    # Format courses into a readable string for the LLM
    courses_formatted = "\n".join([
        f"- Title: {c.get('title', 'N/A')}\n  Link: {c.get('link', 'N/A')}\n  Snippet: {c.get('snippet', 'N/A')}"
        for c in courses
    ])

    chain = ranker_prompt | llm_ranker | parser

    try:
        response = chain.invoke({
            "user_goal": user_goal,
            "current_topic": current_topic,
            "courses_list": courses_formatted
        })
        return response.get('ranked_courses', [])
    except Exception as e:
        print(f"🔴 Error ranking courses: {e}")
        return []

