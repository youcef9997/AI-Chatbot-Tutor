# This service is the final layer of the pipeline.
# It is responsible for sending the prompt to Gemini
# If sending fails, retry.
# if unreachable let user know

import google.generativeai as genai
import time

def configure_gemini(api_key):
    
    genai.configure(api_key=api_key)

# SEND PROMPT TO GEMINI AND RETRY IF UNRECHABLE
def send_to_gemini_with_retry(prompt, retries=3, delay=2):
    
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            gemini_response = model.generate_content(prompt)

            if gemini_response.candidates and len(gemini_response.candidates) > 0:
                return gemini_response.candidates[0].content.parts[0].text

            return gemini_response.text

        except Exception as e:
            print(f"Gemini attempt {attempt + 1} failed:", e, flush=True)

            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print("All Gemini retries failed.", flush=True)
                return "The system is currently busy. Please try again in a moment."