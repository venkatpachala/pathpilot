import streamlit as st
import re
import os # Import os to check for prompts directory

# Import agents
from roadmap_agent import generate_roadmap
from course_search import search_courses
from course_ranker_agent import rank_courses
from follow_up_agent import answer_follow_up_question

st.set_page_config(page_title="PathPilot - AI Roadmap Generator", layout="centered")

# Session state setup
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None
if "last_goal" not in st.session_state:
    st.session_state.last_goal = ""
if "goal_updated" not in st.session_state:
    st.session_state.goal_updated = False
if "show_courses" not in st.session_state:
    st.session_state.show_courses = False
if "show_ranked_courses" not in st.session_state:
    st.session_state.show_ranked_courses = False
if "global_ranked_courses" not in st.session_state:
    st.session_state.global_ranked_courses = None
if "follow_up_response" not in st.session_state:
    st.session_state.follow_up_response = ""
if "follow_up_question_input" not in st.session_state:
    st.session_state.follow_up_question_input = ""


# CSS Styling (Refined for new layout and overall aesthetics)
st.markdown("""
    <style>
    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #0d1117; /* Dark background */
        color: #e6edf3; /* Light text color */
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #161b22; /* Slightly lighter dark for app background */
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    /* Header styling */
    h1 {
        color: #FFD700; /* Gold for main title */
        text-align: center;
        margin-bottom: 0.5rem;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .stSubheader {
        color: #c9d1d9; /* Lighter grey for subheader */
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
    }
    .stMarkdown {
        text-align: center;
        color: #8b949e; /* Muted grey for descriptive text */
        margin-bottom: 2rem;
        font-size: 1rem;
    }

    /* Input area */
    .stTextArea label {
        font-size: 1.15rem;
        color: #FFD700;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .stTextArea textarea {
        background-color: #21262d; /* Darker input background */
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #e6edf3;
        padding: 0.75rem;
    }

    /* Button styling */
    .stButton > button {
        background-color: #FFD700;
        color: #1c1c1c;
        border-radius: 8px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    .stButton > button:hover {
        background-color: #e6c200;
        color: #000000;
        transform: translateY(-2px);
    }

    /* Spinner styling */
    .stSpinner > div > div {
        color: #FFD700;
        font-size: 1.1rem;
    }

    /* Toggle styling */
    .stToggle label {
        color: #e6edf3;
        font-size: 1rem;
    }

    /* Roadmap section styling for expanders */
    .section-expander {
        background-color: #1c1c1c;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #ffd700; /* Thicker border for emphasis */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        overflow: hidden; /* Ensures rounded corners apply to content */
    }
    /* Style for the expander header */
    .st-expanderHeader {
        background-color: #2a2a2a;
        color: #ffd700 !important;
        font-size: 1.25rem; /* Slightly larger heading */
        font-weight: bold;
        padding: 0.9rem 1.2rem;
        border-radius: 10px 10px 0 0;
        border-bottom: 1px solid rgba(255, 215, 0, 0.3);
        cursor: pointer;
    }
    .st-expanderHeader:hover {
        background-color: #333; /* Darken on hover */
    }
    /* Style for the content inside the expander */
    .section-content {
        padding: 1.2rem;
        color: #e2e2e2;
    }
    .section-content strong {
        color: #add8e6; /* Light blue for internal bold labels */
        font-size: 1.05rem;
        display: block; /* Make labels block-level for better spacing */
        margin-top: 0.8rem;
        margin-bottom: 0.3rem;
    }
    .section-content strong:first-child {
        margin-top: 0; /* No top margin for the first label */
    }
    .section-content p, .section-content li {
        font-size: 0.95rem;
        color: #c9d1d9;
        line-height: 1.6;
        margin-bottom: 0.4rem;
    }
    .section-content ul {
        padding-left: 1.5rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .section-content li {
        margin-bottom: 0.2rem;
    }
    .section-content li::marker {
        color: #ffd700;
    }

    /* Special sections (Career Guidance, Total Time) */
    .special-section {
        background-color: #1c1c1c;
        padding: 1.2rem;
        border-radius: 10px;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #87ceeb; /* Different color for special sections */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .special-section h3 {
        font-size: 1.25rem;
        color: #87ceeb; /* Light blue for special section titles */
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(135, 206, 235, 0.3);
        padding-bottom: 0.4rem;
    }
    .special-section p, .special-section li {
        color: #c9d1d9;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .special-section ul {
        padding-left: 1.5rem;
        margin-top: 0.5rem;
    }

    /* Course suggestion specific styling */
    .course-suggestions {
        background-color: #2a2a2a;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 2.5rem; /* More space before course suggestions */
        margin-bottom: 1.5rem;
        border: 1px solid #555555;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .course-suggestions h4 {
        color: #add8e6;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px dashed #444444;
    }
    .course-item {
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px dashed #333; /* Separator for course items */
    }
    .course-item:last-child {
        border-bottom: none; /* No border for the last item */
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .course-item a {
        color: #87ceeb;
        text-decoration: none;
        font-weight: bold;
        font-size: 1rem;
    }
    .course-item a:hover {
        text-decoration: underline;
    }
    .course-item p {
        font-size: 0.9rem;
        color: #cccccc;
        margin-top: 0.4rem;
    }

    /* Info, Warning, Success messages */
    .stWarning, .stInfo, .stSuccess {
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .stWarning {
        background-color: #332b00;
        color: #ffd700;
        border: 1px solid #ffd700;
    }
    .stInfo {
        background-color: #002e5c;
        color: #87ceeb;
        border: 1px solid #87ceeb;
    }
    .stSuccess {
        background-color: #003d1a;
        color: #90ee90;
        border: 1px solid #90ee90;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6a737d;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# UI Header
st.title("🧠 PathPilot")
st.subheader("Your AI-Powered Learning Roadmap Buddy 🚀")
st.markdown("Write your learning goal and get a beautifully structured roadmap with time, tools, projects, and career guidance!")

user_goal = st.text_area("💬 What do you want to learn?", placeholder="e.g. I want to become a backend developer using Python", height=100)

# Check if goal has changed
if user_goal != st.session_state.last_goal:
    st.session_state.goal_updated = True
    st.session_state.last_goal = user_goal
    # Reset all relevant session states when goal changes
    st.session_state.global_ranked_courses = None
    st.session_state.follow_up_response = ""
    st.session_state.follow_up_question_input = "" # Clear follow-up question input
    st.session_state.show_courses = False # Reset course toggles
    st.session_state.show_ranked_courses = False


# Generate roadmap button
if st.button("🎯 Generate Roadmap", use_container_width=True):
    if user_goal.strip() == "":
        st.warning("Please enter a valid goal.")
    else:
        with st.spinner("🛠️ Crafting your custom roadmap with Gemini..."):
            st.session_state.roadmap = generate_roadmap(user_goal)
            st.session_state.goal_updated = False
            # Reset course display and ranking on new roadmap generation
            st.session_state.show_courses = False
            st.session_state.show_ranked_courses = False
            st.session_state.global_ranked_courses = None # Clear previous global ranked courses
            st.session_state.follow_up_response = "" # Clear previous follow-up answer
            st.session_state.follow_up_question_input = "" # Clear follow-up question input after generation

# Course suggestion toggles
if st.session_state.roadmap:
    st.markdown("---") # Visual separator
    st.markdown("#### Explore Further", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        st.session_state.show_courses = st.toggle("🔍 Show overall course suggestions", value=st.session_state.show_courses, key="show_courses_toggle")
    with col2:
        if st.session_state.show_courses:
            st.session_state.show_ranked_courses = st.toggle("✨ Rank courses with AI", value=st.session_state.show_ranked_courses, key="rank_courses_toggle")


# --- Helper function to parse roadmap section content ---
def parse_roadmap_section_content(content: str) -> dict:
    """
    Parses the raw content of a roadmap section into structured components.
    Assumes content follows the format:
    **Topics to Cover:** ...
    **Estimated Time:** ...
    **Key Tools/Technologies:** ...
    **Mini-Projects/Exercises:** ...
    **Resources/Learning Strategies:** ...
    """
    parsed_data = {
        "Topics to Cover": "",
        "Estimated Time": "",
        "Key Tools/Technologies": "",
        "Mini-Projects/Exercises": "",
        "Resources/Learning Strategies": ""
    }

    # Define the markers based on your prompt's bolded labels
    markers = {
        "Topics to Cover": "**Topics to Cover:**",
        "Estimated Time": "**Estimated Time:**",
        "Key Tools/Technologies": "**Key Tools/Technologies:**",
        "Mini-Projects/Exercises": "**Mini-Projects/Exercises:**",
        "Resources/Learning Strategies": "**Resources/Learning Strategies:**"
    }

    # Create a single string with content and markers for easier splitting
    temp_content = content
    for key, marker in markers.items():
        temp_content = temp_content.replace(marker, f"---SPLIT_{key.replace(' ', '_').upper()}---")

    # Split by the custom markers
    parts = re.split(r'---SPLIT_([A-Z_]+)---', temp_content)

    # The first part is usually before the first marker, which we ignore
    # Iterate through parts, looking for our markers and then assigning the subsequent text
    current_key_name = None
    for i, part in enumerate(parts):
        if i % 2 == 1: # This is a marker (e.g., "TOPICS_TO_COVER")
            # Convert marker back to original key name
            current_key_name = part.replace('_', ' ').title()
            if current_key_name not in parsed_data: # Handle unexpected markers
                current_key_name = None
        elif current_key_name: # This is the content following a marker
            parsed_data[current_key_name] = part.strip()
            current_key_name = None # Reset for the next marker

    return parsed_data


if st.session_state.roadmap:
    roadmap_str = str(st.session_state.roadmap)
    st.markdown("## 🧭 Your Personalized Roadmap", unsafe_allow_html=True)

    # Split the roadmap into sections based on potential headings and career guidance
    # The regex tries to capture Level X: ... or **Career Guidance & Next Steps:**
    # It also captures the Total Estimated Time as a separate section if it's at the end
    sections_raw = re.split(r'\n{2,}(?=(?:Level|Phase|Module)\s*\d+[:\-]|\*{2}Career Guidance & Next Steps\*{2}|Total Estimated Time for Roadmap:)', roadmap_str.strip())
    
    # Process each section
    for section_text in sections_raw:
        section_text = section_text.strip()
        if not section_text:
            continue

        # Extract the heading for the expander or direct display
        heading_match = re.match(r'^(.*?)(?:\n|$)', section_text)
        display_heading = "Roadmap Section"
        if heading_match:
            display_heading = heading_match.group(1).strip()
            # Clean up the display heading (remove markdown bolding, emojis for the expander title)
            display_heading = re.sub(r'[\*#\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]', '', display_heading, flags=re.UNICODE).strip()
            # Remove "Estimated Time: (X-Y weeks)" from the expander title if present
            display_heading = re.sub(r'Estimated Time:.*', '', display_heading).strip()
            display_heading = re.sub(r'Total Time Estimate:.*', '', display_heading).strip()

        # Check if it's the Career Guidance section or Total Time Estimate section
        is_career_guidance = "Career Guidance & Next Steps" in display_heading
        is_total_time = "Total Estimated Time for Roadmap:" in section_text
        
        if is_career_guidance or is_total_time:
            # For career guidance and total time, display directly without an expander,
            # but still apply basic markdown formatting
            st.markdown(f'<div class="special-section"><h3>{display_heading}</h3><div class="section-content">', unsafe_allow_html=True)
            # Get content after the heading
            content_to_display = section_text.replace(heading_match.group(0), '', 1).strip() if heading_match else section_text
            # Apply basic markdown to the content (bolding, lists)
            content_to_display = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong>\1</strong>', content_to_display)
            content_to_display = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content_to_display)
            content_to_display = re.sub(r'^\s*([*-])\s*(.*)', r'- \2', content_to_display, flags=re.MULTILINE)
            st.markdown(content_to_display, unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            # For regular learning sections, use an expander
            with st.expander(display_heading, expanded=False): # Start collapsed for less clutter
                st.markdown('<div class="section-content">', unsafe_allow_html=True)
                
                # Get the actual content part by removing the heading line
                content_for_parsing = section_text.replace(heading_match.group(0), '', 1).strip() if heading_match else section_text
                parsed_section = parse_roadmap_section_content(content_for_parsing)

                # Display each parsed component with clear labels
                if parsed_section["Topics to Cover"]:
                    st.markdown(f"**Topics to Cover:** {parsed_section['Topics to Cover']}")
                if parsed_section["Estimated Time"]:
                    st.markdown(f"**Estimated Time:** {parsed_section['Estimated Time']}")
                if parsed_section["Key Tools/Technologies"]:
                    st.markdown(f"**Key Tools/Technologies:** {parsed_section['Key Tools/Technologies']}")
                if parsed_section["Mini-Projects/Exercises"]:
                    st.markdown(f"**Mini-Projects/Exercises:** {parsed_section['Mini-Projects/Exercises']}")
                if parsed_section["Resources/Learning Strategies"]:
                    st.markdown(f"**Resources/Learning Strategies:** {parsed_section['Resources/Learning Strategies']}")
                
                st.markdown('</div>', unsafe_allow_html=True)

    # --- GLOBAL COURSE SUGGESTIONS BLOCK ---
    if st.session_state.show_courses:
        global_search_query = st.session_state.last_goal 
        
        # Only search/rank if we haven't already and the toggles are on
        if st.session_state.global_ranked_courses is None:
            with st.spinner(f"Searching for overall courses related to '{global_search_query}'..."):
                course_results = search_courses(global_search_query, num_results=10) # Get more results for global search

            if course_results:
                if st.session_state.show_ranked_courses:
                    with st.spinner(f"AI is ranking the best courses for your '{global_search_query}' journey..."):
                        courses_for_ranking = [
                            {"title": c["title"], "link": c["link"], "snippet": c["snippet"]}
                            for c in course_results
                        ]
                        st.session_state.global_ranked_courses = rank_courses(st.session_state.last_goal, global_search_query, courses_for_ranking)
                else:
                    st.session_state.global_ranked_courses = course_results
            else:
                st.session_state.global_ranked_courses = [] # No courses found

        # Display the global course results
        if st.session_state.global_ranked_courses is not None:
            st.markdown('<div class="course-suggestions">', unsafe_allow_html=True)
            st.markdown(f"<h4>📚 Recommended Courses for your: {global_search_query} Learning Journey</h4>", unsafe_allow_html=True)

            if not st.session_state.global_ranked_courses:
                st.info(f"No specific courses found for '{global_search_query}'. Try a different overall goal.")
            else:
                if st.session_state.show_ranked_courses:
                    st.success("✅ Courses ranked by AI:")
                    for i, course_info in enumerate(st.session_state.global_ranked_courses, start=1):
                        st.markdown(f'<div class="course-item">', unsafe_allow_html=True)
                        st.markdown(f"**{i}. {course_info['title']}**")
                        st.markdown(f"<p>🔗 <a href='{course_info['link']}' target='_blank'>{course_info['link']}</a></p>", unsafe_allow_html=True)
                        if course_info.get('reason'):
                            st.markdown(f"<p><strong>Reason:</strong> {course_info['reason']}</p>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                else: # Show unranked courses if ranking is not toggled
                    st.info("Displaying unranked course suggestions:")
                    for i, course in enumerate(st.session_state.global_ranked_courses, start=1):
                        with st.expander(f"{i}. {course['title']}"): # Use expander for unranked courses too
                            st.markdown(f'<div class="course-item">', unsafe_allow_html=True)
                            st.markdown(f"<p>🔗 <a href='{course['link']}' target='_blank'>{course['link']}</a></p>", unsafe_allow_html=True)
                            if course.get('snippet'):
                                st.markdown(f"<p>{course['snippet']}</p>", unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Follow-up Question Section ---
    st.markdown("---") # Separator for clarity
    st.markdown("## ❓ Ask PathPilot a Follow-up Question", unsafe_allow_html=True)

    if not st.session_state.roadmap:
        st.info("Generate a roadmap first to ask follow-up questions.")
        st.session_state.follow_up_question_input = "" # Clear input if roadmap is not there
    else:
        # Use a key to ensure Streamlit tracks changes properly for this text_area
        follow_up_question = st.text_area(
            "Ask a question about your roadmap or learning path:",
            value=st.session_state.get('follow_up_question_input', ''), # Retrieve stored value
            key="follow_up_question_text_area",
            height=70,
            placeholder="e.g., 'What are the main topics in Level 3?' or 'What kind of projects should I focus on?'"
        )
        
        # Update session state with current input value
        st.session_state.follow_up_question_input = follow_up_question

        if st.button("💬 Ask PathPilot", use_container_width=True):
            if follow_up_question.strip() == "":
                st.warning("Please enter your question.")
            else:
                with st.spinner("🤔 Thinking..."):
                    # Call the new follow-up agent
                    response = answer_follow_up_question(
                        st.session_state.roadmap,
                        st.session_state.last_goal,
                        follow_up_question
                    )
                    st.session_state.follow_up_response = response
        
        # Display the AI's response
        if st.session_state.follow_up_response:
            st.markdown(f'<div class="special-section" style="margin-top: 1rem;"><h3>PathPilot Says:</h3><div class="section-content">{st.session_state.follow_up_response}</div></div>', unsafe_allow_html=True)


st.markdown("---")
st.markdown('<div class="footer">🛠️ Built with LangChain + Gemini | ❤️ Designed for Indian learners by Venkat</div>', unsafe_allow_html=True)

