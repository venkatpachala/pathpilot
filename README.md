PathPilot is your personalized AI-powered course and career roadmap navigator.
It helps learners discover the most relevant learning paths and curated course suggestions across platforms like
Udemy, Coursera, Skillshare, and more — all aligned with their domain interests and latest tech trends.

Key Features

- AI-based skill roadmap generation
- Real-time web scraping for course suggestions
- Intelligent ranking of free & paid courses
- Interactive tree view of tech goals
- Progress tracking for roadmap sections
- Toggle between "Beginner → Expert" and "Job-Ready in 90 Days" modes
- ⚙Built using Streamlit, LangChain, Gemini API
- Backend logic powered by Python

Tech Stack

- Frontend: Streamlit
- Backend: Python, LangChain, Gemini 1.5 Flash
- Deployment: Vercel/Render (Not done yet)
- Database (Coming Soon): Supabase / PostgreSQL

## API Server

A FastAPI server exposes the core agents so external frontends (e.g., Next.js) can consume them.

### Endpoints
- `POST /api/generate_roadmap` → returns roadmap sections for a goal.
- `GET /api/search_courses?topic=...` → searches the web for related courses.
- `POST /api/rank_courses` → ranks a list of courses for a goal.
- `POST /api/follow_up` → answers follow‑up questions based on a roadmap.

### Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Phase 2 in Progress
I'm working on:
- Web search & summarization for dynamic course recommendations
- Personalized recommendations based on user goals
- AI agent for natural chat-based interaction

Idea Behind It

Learners are overwhelmed by too many courses and lack of direction.
PathPilot bridges this gap with a smart assistant that guides users step-by-step from choosing a domain to mastering the right tools with verified, high-quality learning material.

Feedback & Contributions

Found a bug or want to suggest a feature? Create an issue or submit a pull request. Let’s build something impactful together!
