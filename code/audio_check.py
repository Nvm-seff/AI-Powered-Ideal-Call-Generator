import os
import sys
# Use the specific client class
from elevenlabs.client import ElevenLabs
# Corrected import: Use 'ApiError' (lowercase 'i') and remove RateLimitError for now
from elevenlabs.client import ApiError # <--- CORRECTED IMPORT
from elevenlabs import play # Optional
import code.config as config

API_KEY = config.ELEVENLABS_API_KEY
AGENT_ID = config.AGENT_VOICE_ID
PATIENT_ID = config.PATIENT_VOICE_ID
TRANSCRIPT_FILE = "sample_transcript_ideal_call_rag.txt"
OUTPUT_FILENAME = "sample_output_for_cloning.mp3"
MODEL_ID = "eleven_multilingual_v2" # Or "eleven_monolingual_v1"

# --- Validation ---
if not API_KEY:
    print("Error: ELEVENLABS_API_KEY not found in environment variables (.env file).")
    sys.exit(1)
# ... (add checks for AGENT_ID and PATIENT_ID back if you removed them) ...
if not AGENT_ID:
    print("Error: AGENT_ID not found in environment variables (.env file).")
    sys.exit(1)
if not PATIENT_ID:
    print("Error: PATIENT_ID not found in environment variables (.env file).")
    sys.exit(1)

print("Configuration loaded successfully.")
print(f" - AGENT Voice ID: {AGENT_ID}")
print(f" - PATIENT Voice ID: {PATIENT_ID}")
print(f" - Using Model: {MODEL_ID}")
print(f" - Transcript: {TRANSCRIPT_FILE}")
print(f" - Output File: {OUTPUT_FILENAME}")


# --- Initialize ElevenLabs Client ---
try:
    client = ElevenLabs(api_key=API_KEY)
    print("ElevenLabs client initialized successfully.")
except Exception as e:
    print(f"Error initializing ElevenLabs client: {e}")
    sys.exit(1)

# --- Read and Parse Transcript ---
try:
    with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"Successfully read {len(lines)} lines from '{TRANSCRIPT_FILE}'.")
except FileNotFoundError:
    print(f"Error: Transcript file '{TRANSCRIPT_FILE}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading transcript file: {e}")
    sys.exit(1)

# --- Process Lines and Generate Audio ---
all_audio_bytes = []

print("\nStarting audio generation...")
for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue

    speaker_text = ""
    voice_id = None
    speaker_label = "Unknown"

    if line.startswith("AGENT:"):
        speaker_text = line.replace("AGENT:", "", 1).strip()
        voice_id = AGENT_ID
        speaker_label = "AGENT"
    elif line.startswith("PATIENT:"):
        speaker_text = line.replace("PATIENT:", "", 1).strip()
        voice_id = PATIENT_ID
        speaker_label = "PATIENT"
    else:
        print(f"Warning: Skipping unrecognized line format (line {i+1}): {line}")
        continue

    if not speaker_text:
        print(f"Warning: Skipping line with speaker label but no text (line {i+1}): {line}")
        continue

    print(f" - Processing line {i+1} ({speaker_label}): '{speaker_text[:50]}...'")

    try:
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=speaker_text,
            model_id=MODEL_ID
        )
        line_audio_bytes = b"".join(audio_stream)
        all_audio_bytes.append(line_audio_bytes)

    # Removed specific RateLimitError block
    # Use ApiError with correct capitalization
    except ApiError as e: # <--- CORRECTED CASE in except block
        print(f"Error: ElevenLabs API error processing line {i+1} ('{line}') with voice {voice_id}: {e}")
        # You can potentially check e.status_code or str(e) here if you need to know if it was a rate limit
        # For example: if hasattr(e, 'status_code') and e.status_code == 429: print("   (This was likely a rate limit error)")
        print("       Please check your API key, voice ID, model ID, and account status/quota.")
        sys.exit(1) # Decide if you want to exit on the first error
    except Exception as e:
        print(f"Error: An unexpected error occurred processing line {i+1}: {e}")
        # Consider if you want to sys.exit(1) here too, or maybe just continue
        sys.exit(1) # Exiting for now

# --- Combine Audio Chunks and Save to File ---
if not all_audio_bytes:
    print("\nNo audio was generated (transcript might be empty or all lines skipped).")
    sys.exit(0)

print(f"\nCombining {len(all_audio_bytes)} audio segments...")
try:
    with open(OUTPUT_FILENAME, "wb") as f:
        for audio_chunk in all_audio_bytes:
            f.write(audio_chunk)
    print(f"\n✅ Combined audio successfully saved as: {OUTPUT_FILENAME}")

    # Optional: Play the generated audio
    # print("Playing generated audio...")
    # play(b"".join(all_audio_bytes))

except Exception as e:
    print(f"Error writing combined audio to file '{OUTPUT_FILENAME}': {e}")
    sys.exit(1)