# gemini_client.py
import google.generativeai as genai
import code.config as config # Import config for API key and model settings
from google.generativeai.types import GenerationConfig # For more detailed config

def configure_gemini():
    """Configures the Google Generative AI client."""
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        print("Gemini client configured successfully.")
        return True
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
        return False

def generate_analysis(prompt: str) -> str | None:
    """
    Sends the prompt to the configured Gemini model and retrieves the analysis.

    Args:
        prompt: The prompt string containing transcript, KPIs, and instructions.

    Returns:
        The raw text response from the Gemini API, or None if an error occurs.
    """
    if not configure_gemini(): # Ensure client is configured before each call (or configure once globally)
         return None

    print(f"Sending request to Gemini model: {config.GEMINI_MODEL_NAME}...")
    try:
        model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)
        generation_config = GenerationConfig(
            temperature=config.GEMINI_TEMPERATURE,
            max_output_tokens=config.GEMINI_MAX_OUTPUT_TOKENS,
            # response_mime_type="application/json" # Try enabling this if model supports it well!
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        print("Received response from Gemini.")
        # Basic check if response has text part
        if response.parts:
             # Accessing the text content safely
             # Sometimes response might just have safety ratings or finish reason
            response_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            if response_text:
                return response_text
            else:
                print("Warning: Gemini response received but contains no text part.")
                # Log the full response for debugging if needed
                # print("Full Gemini Response:", response)
                return None
        else:
            print("Warning: Gemini response received but has no parts.")
            # Log the full response for debugging if needed
            # print("Full Gemini Response:", response)
            return None

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # You might want to inspect the specific error type for more details
        # For example, handle ResourceExhaustedError, InvalidArgumentError etc.
        # print(f"Gemini API Error Details: {getattr(e, 'response', 'No response details')}")
        return None

# --- Example Usage (Optional) ---
# if __name__ == "__main__":
#     test_prompt = "Explain the concept of RAG in large language models in one sentence."
#     result = generate_analysis(test_prompt)
#     if result:
#         print("\n--- Gemini Response ---")
#         print(result)
#     else:
#         print("\nFailed to get response from Gemini.")