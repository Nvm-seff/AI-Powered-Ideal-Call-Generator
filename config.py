# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please create a .env file.")

# You can adjust the model name if needed
# Check Google AI Studio or documentation for available models (e.g., gemini-1.5-pro)
GEMINI_MODEL_NAME = "gemini-1.5-flash" # Good balance of capability and speed/cost

# Define speaker labels (adjust if your diarization uses different labels)
AGENT_SPEAKER_LABEL = "AGENT" # Or "SPEAKER_01", "Rep", etc.
PATIENT_SPEAKER_LABEL = "PATIENT" # Or "SPEAKER_02", "Caller", etc.

# Response generation settings (adjust as needed)
GEMINI_TEMPERATURE = 0.2 # Lower temperature for more deterministic, factual analysis
GEMINI_MAX_OUTPUT_TOKENS = 8192 # Generous limit for JSON output, adjust based on model/needs