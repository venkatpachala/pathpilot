import os
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# --- Debugging: Verify API Key Loading ---
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("WARNING: GOOGLE_API_KEY not found in environment variables for follow_up_agent.py!")
else:
    print("DEBUG: GOOGLE_API_KEY loaded successfully in follow_up_agent.py")
# --- End Debugging ---

def answer_follow_up_question(roadmap_text: str, user_goal: str, question: str) -> str:
    """
    Answers a follow-up question based on the provided roadmap text.

    Args:
        roadmap_text (str): The full text of the generated roadmap.
        user_goal (str): The original learning goal of the user.
        question (str): The user's follow-up question.

    Returns:
        str: The AI's answer to the question.
    """
    if not roadmap_text or not question:
        return "Please generate a roadmap and ask a valid question."

    # 1. Create a LangChain Document from the roadmap text
    doc = Document(page_content=roadmap_text, metadata={"source": "roadmap"})

    # 2. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents([doc])

    # 3. Create embeddings and a vector store
    # FIX: Added leading underscore to '_docs' to prevent hashing error
    @st.cache_resource(ttl="1h") 
    def get_vector_store(_docs): # Changed 'docs' to '_docs'
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
        vector_store = FAISS.from_documents(_docs, embeddings) # Use '_docs' here too
        return vector_store

    vector_store = get_vector_store(chunks) # Pass 'chunks' as before

    # 4. Define the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=google_api_key)

    # 5. Create a RetrievalQA chain
    template = """
    You are an AI assistant specialized in providing guidance based on a learning roadmap.
    Your task is to answer the user's follow-up question ONLY using the provided learning roadmap context.
    If the answer cannot be found in the roadmap context, politely state that the information is not available in the roadmap.

    User's original learning goal: {user_goal}
    User's follow-up question: {question}

    Roadmap Context:
    {context}

    Answer:
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}), # Retrieve top 3 relevant chunks
        return_source_documents=False,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )

    # 6. Invoke the chain to get the answer
    try:
        response = qa_chain.invoke({"query": question, "user_goal": user_goal, "question": question})
        return response.get("result", "I couldn't find an answer to that question within the generated roadmap.")
    except Exception as e:
        print(f"An error occurred while answering the follow-up question: {e}")
        return "Sorry, I encountered an issue while processing your question. Please try again."

if __name__ == '__main__':
    # This block is for testing the agent independently.
    # Set your GOOGLE_API_KEY environment variable for testing
    # os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY" # Replace with your actual key for local testing

    test_roadmap = """
    Level 1: Python Fundamentals (4 weeks)
    **Topics to Cover:** Variables, Data Types, Control Flow (if/else, loops), Functions, Basic Data Structures (Lists, Dictionaries, Tuples, Sets), Object-Oriented Programming (Classes, Objects, Inheritance), Error Handling.
    **Estimated Time:** 160 hours (4 weeks at 40 hours/week)
    **Key Tools/Technologies:** Python 3, VS Code or PyCharm, Git.
    **Mini-Projects/Exercises:** Simple Calculator, To-Do List App (CLI), Basic Banking System (OOP).
    **Resources/Learning Strategies:** Online tutorials (e.g., Real Python, FreeCodeCamp), "Python Crash Course" book.

    Level 2: Web Frameworks (Django/Flask) (6 weeks)
    **Topics to Cover:** Introduction to Web Development, HTTP Basics, RESTful APIs, Django (Models, Views, Templates, URLs, Admin), ORM, User Authentication.
    **Estimated Time:** 240 hours (6 weeks at 40 hours/week)
    **Key Tools/Technologies:** Django/Flask, PostgreSQL/SQLite, Postman, Heroku (for deployment).
    **Mini-Projects/Exercises:** Blog API, Simple E-commerce Backend.
    **Resources/Learning Strategies:** Django/Flask official docs, Udemy courses on Django REST Framework.

    **Career Guidance & Next Steps:**
    * Advice on job roles related to the goal: Junior Backend Developer, Python Developer.
    * Tips for building a portfolio: Create 3-5 strong projects, host them on GitHub.
    * Networking strategies: Attend meetups, connect on LinkedIn.
    * Continuous learning advice: Stay updated with new Python versions and framework updates.
    * Important soft skills: Problem-solving, communication, teamwork.

    Total Estimated Time for Roadmap: 10 weeks (400 hours)
    """
    
    test_goal = "Become a backend developer using Python"
    
    print("--- Testing Follow-up Agent ---")
    print("\nQuestion 1: What is the estimated time for Level 1?")
    answer = answer_follow_up_question(test_roadmap, test_goal, "What is the estimated time for Level 1?")
    print(f"Answer: {answer}")

    print("\nQuestion 2: What are the key tools for Level 2?")
    answer = answer_follow_up_question(test_roadmap, test_goal, "What are the key tools for Level 2?")
    print(f"Answer: {answer}")

    print("\nQuestion 3: What is the meaning of life?")
    answer = answer_follow_up_question(test_roadmap, test_goal, "What is the meaning of life?")
    print(f"Answer: {answer}")

    print("\nQuestion 4: What job roles are related to this goal?")
    answer = answer_follow_up_question(test_roadmap, test_goal, "What job roles are related to this goal?")
    print(f"Answer: {answer}")
