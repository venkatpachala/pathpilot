import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def search_courses(topic: str, num_results=10): # Increased default num_results for global search
    """
    Searches for online courses related to a given topic using Serper.dev's Google Search API.

    Args:
        topic (str): The topic for which to search courses (e.g., "Python basics").
        num_results (int): The maximum number of search results to retrieve.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a course
                    and contains 'title', 'link', and 'snippet'.
                    Returns an empty list if an error occurs or no results are found.
    """
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"), # Ensure SERPER_API_KEY is set in your .env
        "Content-Type": "application/json"
    }

    # Construct the search query, explicitly targeting popular course platforms
    # This helps in getting more relevant course results
    data = {
        "q": f"{topic} course site:udemy.com OR site:coursera.org OR site:edx.org OR site:freecodecamp.org OR site:pluralsight.com OR site:linkedin.com/learning OR site:datacamp.com OR site:khanacademy.org",
        "num": num_results
    }

    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        results = response.json().get("organic", []) # Extract organic search results
        
        # Format results into a consistent dictionary structure
        formatted_results = [{
            "title": r["title"],
            "link": r["link"],
            "snippet": r.get("snippet", "") # Use .get to avoid KeyError if snippet is missing
        } for r in results]
        
        return formatted_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error during API request to Serper.dev: {e}")
        # Optionally, log the full response for more details: print(response.text)
        return []
    except KeyError:
        print("Error parsing Serper.dev response: 'organic' key not found or unexpected structure.")
        # print(response.json()) # Uncomment to see the problematic JSON response
        return []
    except Exception as e:
        print(f"An unexpected error occurred during course search: {e}")
        return []

