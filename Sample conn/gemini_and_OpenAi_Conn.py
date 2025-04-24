import os
from dotenv import load_dotenv
import google.generativeai as genai
import openai
from openai import OpenAI, RateLimitError
import time # Import time for potential delays if needed

# Load environment variables
load_dotenv()

# --- Gemini Configuration ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables!")
try:
    genai.configure(api_key=gemini_api_key)
    # Initialize the Gemini model
    # Using gemini-1.5-flash as it's often faster and cheaper for simple tasks
    # You can change back to 'models/gemini-1.5-pro-latest' or your previous model if needed
    gemini_model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    gemini_model = None # Set model to None if configuration fails

# --- OpenAI Configuration (kept for later use) ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found, OpenAI features will be unavailable.")
    client = None
    openai_enabled = False
else:
    try:
        openai.api_key = openai_api_key
        client = OpenAI(api_key=openai_api_key)
        openai_enabled = True
        print("OpenAI API configured successfully.")
    except Exception as e:
        print(f"Error configuring OpenAI API: {e}")
        client = None
        openai_enabled = False


# --- Processing Functions ---

def process_text_input_gemini(user_input):
    """Sends input to the Gemini model and returns the text response."""
    if not gemini_model:
        return "Error: Gemini model not initialized."
    try:
        # Increased safety settings slightly for general queries
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = gemini_model.generate_content(
            user_input,
            safety_settings=safety_settings
            )
        # Check if the response has text content before accessing it
        if response.parts:
             return response.text.strip()
        elif response.prompt_feedback.block_reason:
             return f"Error: Content blocked by Gemini. Reason: {response.prompt_feedback.block_reason}"
        else:
             # Handle cases where response might be empty without a block reason (less common)
             return "Error: Gemini returned an empty response."
    except Exception as e:
        # Catch potential API errors (e.g., connection issues, invalid requests)
        return f"Error interacting with Gemini API: {e}"


# OpenAI function (kept for later use)
def process_text_input_openai(user_input):
    """Sends input to the OpenAI model and returns the text response."""
    if not openai_enabled or not client:
        return "Error: OpenAI client not initialized or key missing."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or specify another model like gpt-4o-mini
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()

    except RateLimitError as e:
        return f"Error: Rate limit exceeded. Check OpenAI usage/billing. Details: {e}"
    except openai.APIConnectionError as e:
        return f"OpenAI API request failed to connect: {e}"
    except openai.APIStatusError as e:
        return f"OpenAI API returned an error status code: {e.status_code} - {e.response}"
    except Exception as e:
        return f"An unexpected error occurred with OpenAI: {e}"


def list_available_models_gemini():
    """Lists available Gemini models."""
    if not gemini_model:
        print("Gemini model not initialized.")
        return
    try:
        print("\n--- Available Gemini Models ---")
        models = genai.list_models()
        # Filter for models supporting generateContent for text tasks
        generative_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        if not generative_models:
            print("No generative models found.")
            return
        for model in generative_models:
            # Basic check for text generation capability (might need refinement based on specific model features)
            print(f"- {model.name} (Display Name: {model.display_name})")
            # print(f"  Description: {model.description}") # Uncomment for more detail
        print("-----------------------------\n")
    except Exception as e:
        print(f"Error listing Gemini models: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    prompt_file = "prompts.txt"
    print(f"Attempting to read prompts from: {prompt_file}")

    # Optional: List available Gemini models on startup
    # list_available_models_gemini()

    if not gemini_model:
        print("Exiting: Gemini model could not be initialized.")
    else:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts = f.readlines()

            if not prompts:
                print(f"Warning: '{prompt_file}' is empty.")
            else:
                print(f"\n--- Processing prompts from {prompt_file} using Gemini ---")
                for i, prompt in enumerate(prompts):
                    cleaned_prompt = prompt.strip() # Remove leading/trailing whitespace and newline
                    if not cleaned_prompt or cleaned_prompt.startswith('#'): # Skip empty lines and comments
                        continue

                    print(f"\n[{i+1}] Prompt: {cleaned_prompt}")
                    gemini_answer = process_text_input_gemini(cleaned_prompt)
                    print(f"Gemini Response: {gemini_answer}")
                    # Optional: Add a small delay between API calls if needed
                    # time.sleep(1)

                print("\n--- Finished processing all prompts ---")

        except FileNotFoundError:
            print(f"Error: File '{prompt_file}' not found. Please create it in the same directory as the script, with one prompt per line.")
        except Exception as e: # Catch other potential errors during file reading or processing
            print(f"An unexpected error occurred: {e}")

    # --- Example of how you might use OpenAI later (currently commented out) ---
    # if openai_enabled:
    #     simulated_transcription = "What is the capital of Spain?"
    #     print("\n--- Testing OpenAI ---")
    #     openai_answer = process_text_input_openai(simulated_transcription)
    #     print(f"Prompt: {simulated_transcription}")
    #     print(f"OpenAI Response: {openai_answer}")
    # else:
    #     print("\nOpenAI processing skipped (not enabled or configured).")