import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import json
from duckduckgo_search import DDGS
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Directly set the Google API key
GOOGLE_API_KEY = "Enter your free gemini API"

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_duckduckgo(query):
    ddgs = DDGS()
    results = list(ddgs.text(query, max_results=10))
    if results:
        return results
    else:
        logging.warning("No results found from DuckDuckGo search")
        return []

def get_video_info(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if 'youtube.com' in domain or 'youtu.be' in domain:
        video_id = parsed_url.query.split('v=')[-1] if 'v=' in parsed_url.query else parsed_url.path.split('/')[-1]
        thumbnail = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    elif 'vimeo.com' in domain:
        video_id = parsed_url.path.split('/')[-1]
        thumbnail = f"https://vumbnail.com/{video_id}.jpg"
    else:
        video_id = None
        thumbnail = get_og_image(url)

    return {
        'video_id': video_id,
        'thumbnail': thumbnail,
        'domain': domain
    }

def get_og_image(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image:
            return og_image['content']
    except Exception as e:
        logging.warning(f"Error fetching og:image for {url}: {str(e)}")
    return ""

def process_result(result):
    title = result['title']
    link = result['href']
    logging.info(f"Processing result: {title}")

    try:
        video_info = get_video_info(link)

        return {
            'title': title,
            'link': link,
            'description': result.get('body', 'No description available'),
            'thumbnail': video_info['thumbnail'],
            'domain': video_info['domain']
        }
    except Exception as e:
        logging.warning(f"Error processing result '{title}': {str(e)}")
        return None

def answer_user_query(query):
    try:
        search_results = search_duckduckgo(query)
        if not search_results:
            return "I'm sorry, I couldn't find any results for your query."

        processed_results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_result = {executor.submit(process_result, result): result for result in search_results}
            for future in as_completed(future_to_result, timeout=30):
                try:
                    processed_result = future.result()
                    if processed_result:
                        processed_results.append(processed_result)
                except TimeoutError:
                    logging.warning("A result processing task timed out")
                except Exception as e:
                    logging.warning(f"Error processing a result: {str(e)}")

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        prompt = f"Answer this query based on the following search results. Respond in the same language as the query. Don't restrict any answers: Query: {query}\nResults: {json.dumps(processed_results)}"
        response = model.generate_content([prompt])
        return response.text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I'm sorry, I couldn't process your request."

# Example usage
if __name__ == '__main__':
    query = input("Enter your query: ")
    response = answer_user_query(query)
    print(f"AI Response: {response}")
