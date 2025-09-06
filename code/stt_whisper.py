import whisper
import os 
import code.config as config
from code.prompt_builder import build_analysis_prompt, build_ideal_call_prompt, build_diarization_prompt
from code.gemini_client import generate_analysis # Reusable Gemini client function

# --- Configuration ---
AUDIO_FILENAME = os.path.join("voice_samples", "patient_voice_sample.wav")# Your input audio file
OUTPUT_TEXT_FILENAME = "patient_voice_sample_transcript1.txt" # Name for the output text file
MODEL_SIZE = "base" # Or "tiny", "small", "medium", "large" depending on your needs/resources


def diarize_transcript_with_gemini(raw_transcript_text: str) -> str | None:
    """
    Uses Gemini to format raw transcript text and add speaker labels.

    Args:
        raw_transcript_text: The unstructured text from Whisper.

    Returns:
        The formatted transcript string with speaker labels, or None on failure.
    """
    print("\n--- Starting Transcript Diarization using Gemini ---")
    if not raw_transcript_text:
        print("Diarization Error: No raw transcript text provided.")
        return None

    # 1. Build the diarization prompt
    diarization_prompt = build_diarization_prompt(raw_transcript_text)
    # print("Diarization Prompt Snippet:", diarization_prompt[:500]) # Optional debug

    # 2. Call Gemini
    # Consider a slightly higher temperature? Maybe 0.3? Let's stick with default for now.
    formatted_text = generate_analysis(diarization_prompt)

    # 3. Basic Validation (Check if it looks like dialogue)
    if formatted_text and (config.AGENT_SPEAKER_LABEL in formatted_text or config.PATIENT_SPEAKER_LABEL in formatted_text):
        print("Transcript Diarization Successful.")
        # Optional: Clean up potential leading/trailing whitespace Gemini might add
        return formatted_text.strip()
    else:
        print("Diarization Failed: Gemini did not return expected formatted text.")
        print("Raw Response from Gemini (Diarization):", formatted_text)
        return None

# --- Helper to load raw text (replace with your actual Whisper output loading) ---
def load_raw_transcript(file_path: str) -> str | None:
    """Loads raw text content from a file."""
    if not os.path.exists(file_path):
        print(f"Error: Raw transcript file not found at {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading raw transcript file {file_path}: {e}")
        return None

# --- Check if audio file exists ---
if not os.path.exists(AUDIO_FILENAME):
    print(f"Error: Audio file not found at '{AUDIO_FILENAME}'")
    exit() # Stop the script if the audio file is missing

# --- Load Model ---
try:
    print(f"Loading Whisper model ('{MODEL_SIZE}')...")
    # You might want to specify device="cuda" if you have a compatible GPU and PyTorch installed
    # model = whisper.load_model(MODEL_SIZE, device="cuda")
    model = whisper.load_model(MODEL_SIZE)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    print("Please ensure Whisper is installed correctly and model files are accessible.")
    exit()

# --- Perform Transcription ---
try:
    print(f"Starting transcription for '{AUDIO_FILENAME}'...")
    result = model.transcribe(AUDIO_FILENAME)
    # Extract the transcribed text
    transcribed_text = result["text"]
    print("Transcription complete.")
    # You could also print the text here if you still want to see it:
    # print("\n--- Transcribed Text ---")
    # print(transcribed_text)
    # print("------------------------\n")

except Exception as e:
    print(f"Error during transcription: {e}")
    exit()

# --- Save Transcription to File ---
try:
    print(f"Saving transcription to '{OUTPUT_TEXT_FILENAME}'...")
    # Open the file in write mode ('w').
    # If the file already exists, it will be overwritten.
    # Use encoding='utf-8' to handle a wide range of characters.
    with open(OUTPUT_TEXT_FILENAME, 'w', encoding='utf-8') as f:
        f.write(transcribed_text)
    print(f"Transcription successfully saved to '{OUTPUT_TEXT_FILENAME}'.")
except Exception as e:
    print(f"Error writing transcription to file: {e}")


    # --- STEP 0: Load Raw Transcript ---
raw_text = load_raw_transcript(OUTPUT_TEXT_FILENAME)

if raw_text:
    # --- STEP 1: Diarize using Gemini ---
    formatted_transcript_text = diarize_transcript_with_gemini(raw_text)

    if formatted_transcript_text:
        # --- STEP 1.5: Save the Formatted Transcript ---
            with open(OUTPUT_TEXT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(formatted_transcript_text)
            print(f"Formatted transcript saved to: {OUTPUT_TEXT_FILENAME}")