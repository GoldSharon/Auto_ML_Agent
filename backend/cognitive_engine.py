import json
import time
import os 
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))


def chat_llm(system_instructions: str,
             user_input: str,
             max_retries: int = 5) -> dict:
    
    """Sends a query to the LLM with exponential backoff for 503 and 429 errors."""
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
               
                model = os.getenv("LLM_MODEL_NAME"),
                config=types.GenerateContentConfig(
                    system_instruction=system_instructions,
                    temperature=0.3,
                    response_mime_type="application/json"
                ),
                contents=user_input
            )

            print(os.getenv("LLM_MODEL_NAME"))

            # Successfully got a response
            if response.text:
                try:
                    data = json.loads(response.text)
                    return data
                except json.JSONDecodeError:
                    print("Error: Model did not return valid JSON.")
                    return {}
            
            return {}

        except (errors.ServerError, errors.ClientError) as e:
            # Check for 503 (Overloaded) or 429 (Rate Limit)
            error_str = str(e).upper()
            if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str:
                # Exponential backoff: Wait 2, 4, 8, 16... seconds
                wait_time = (2 ** attempt) + 2 
                print(f"Server busy or Limit hit (Attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # If it's a different error (like Auth or Model name), stop immediately
                print(f"An unexpected API error occurred: {e}")
                break
                
    print("Failed to get a response after maximum retries.")
    return {}

if __name__ == "__main__":
    query = "Tell about cheese cake"

    system_prompt = "Respond in JSON format ."
    
    response = chat_llm(user_input=query, system_instructions=system_prompt)
    
    print(response)
    print(type(response))

