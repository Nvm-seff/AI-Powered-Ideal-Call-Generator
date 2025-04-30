# tts_generator.py
import os
import config
from elevenlabs.client import ElevenLabs # Correct client import
# Removed 'play', 'save' imports as we'll handle saving manually from the stream

def generate_audio_from_script(script_text: str, output_filename: str):
    """
    Generates an audio file from a script with speaker labels using ElevenLabs v1.0+ SDK.
    Streams audio directly to the output file.

    Args:
        script_text: The full text script with AGENT: and PATIENT: labels.
        output_filename: The path to save the resulting audio file (e.g., "output.mp3").

    Returns:
        True if successful, False otherwise.
    """
    # --- Keep initial checks for keys and voice IDs ---
    if not config.ELEVENLABS_API_KEY:
        print("Error: ElevenLabs API Key is not configured in config.py or .env file.")
        return False
    if not config.AGENT_VOICE_ID or config.AGENT_VOICE_ID.startswith("YOUR_"):
        print(f"Error: AGENT_VOICE_ID ('{config.AGENT_VOICE_ID}') is not configured correctly in config.py.")
        return False
    if not config.PATIENT_VOICE_ID or config.PATIENT_VOICE_ID.startswith("YOUR_"):
        print(f"Error: PATIENT_VOICE_ID ('{config.PATIENT_VOICE_ID}') is not configured correctly in config.py.")
        return False

    try:
        print(f"Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

        print(f"Processing script for TTS generation (streaming to {output_filename})...")

        # --- Open the output file in binary write mode BEFORE the loop ---
        with open(output_filename, "wb") as output_file:
            lines = script_text.strip().split('\n')
            segment_count = 0

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                speaker = None
                text_to_speak = ""
                voice_id = None

                if line.startswith(f"{config.AGENT_SPEAKER_LABEL}:"):
                    speaker = config.AGENT_SPEAKER_LABEL
                    text_to_speak = line[len(config.AGENT_SPEAKER_LABEL)+1:].strip()
                    voice_id = config.AGENT_VOICE_ID
                elif line.startswith(f"{config.PATIENT_SPEAKER_LABEL}:"):
                    speaker = config.PATIENT_SPEAKER_LABEL
                    text_to_speak = line[len(config.PATIENT_SPEAKER_LABEL)+1:].strip()
                    voice_id = config.PATIENT_VOICE_ID
                else:
                    print(f"  Skipping line {line_num+1} (no speaker label): '{line[:60]}...'")
                    continue # Skip lines without standard labels

                if not text_to_speak:
                    print(f"  Skipping empty utterance for speaker {speaker} on line {line_num+1}.")
                    continue

                print(f"  Generating audio stream for {speaker} (line {line_num+1}): '{text_to_speak[:50]}...'")
                try:
                    # --- Use the new client.text_to_speech.convert method ---
                    # --- Note: parameter is 'model_id', not 'model' ---
                    audio_stream = client.text_to_speech.convert(
                        voice_id=voice_id,
                        model_id=config.ELEVENLABS_MODEL,
                        text=text_to_speak,
                        # output_format="mp3_44100_128" # Optional: Specify format if needed
                    )

                    # --- Stream the audio chunks directly to the file ---
                    chunk_count = 0
                    for chunk in audio_stream:
                        if chunk: # Ensure chunk is not empty
                           output_file.write(chunk)
                           chunk_count += 1

                    if chunk_count == 0:
                         print(f"  Warning: Received no audio chunks for line {line_num+1}.")
                    else:
                         segment_count += 1

                except Exception as api_e:
                    print(f"  ERROR generating audio stream for line {line_num+1}: '{line[:60]}...'. Error: {api_e}")
                    # Decide whether to stop or continue
                    # return False # Option: Stop on first error
                    continue # Option: Skip failed segment and continue with next line

            # --- End of loop ---
            if segment_count == 0:
                print("Error: No audio segments were successfully generated and written.")
                # Close the file handle explicitly before returning False (though 'with' does it)
                output_file.close()
                # Optionally remove the empty/incomplete file
                if os.path.exists(output_filename):
                     try: os.remove(output_filename)
                     except: pass
                return False

        # --- File is automatically closed here by 'with open(...)' ---
        print(f"\nAudio stream successfully written to: {output_filename} ({segment_count} segments processed).")
        return True

    except IOError as io_e:
         print(f"Error opening or writing to file {output_filename}: {io_e}")
         return False
    except Exception as e:
        print(f"An unexpected error occurred during TTS generation: {e}")
        return False