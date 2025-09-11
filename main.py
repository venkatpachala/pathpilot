from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from roadmap_agent import generate_roadmap
from course_search import search_courses
from course_ranker_agent import rank_courses
from follow_up_agent import answer_follow_up_question

app = FastAPI(title="PathPilot API")


class GoalRequest(BaseModel):
    goal: str
    mode: str | None = "Beginner → Expert"


class RoadmapResponse(BaseModel):
    sections: List[str]


@app.post("/api/generate_roadmap", response_model=RoadmapResponse)
def create_roadmap(req: GoalRequest):
    """Generate a roadmap for the provided goal."""
    roadmap = generate_roadmap(req.goal)
    # split roadmap into sections by blank lines
    sections = [s.strip() for s in roadmap.split("\n\n") if s.strip()]
    return {"sections": sections}


@app.get("/api/search_courses")
def search_courses_endpoint(topic: str):
    """Search for courses related to the topic."""
    return search_courses(topic)


class RankRequest(BaseModel):
    goal: str
    courses: List[Dict]


@app.post("/api/rank_courses")
def rank_courses_endpoint(req: RankRequest):
    """Rank a list of courses for the user's goal."""
    return rank_courses(req.goal, req.goal, req.courses)


class FollowUpRequest(BaseModel):
    roadmap: str
    goal: str
    question: str


@app.post("/api/follow_up")
def follow_up_endpoint(req: FollowUpRequest):
    """Answer a follow-up question about the generated roadmap."""
    answer = answer_follow_up_question(req.roadmap, req.goal, req.question)
    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
