# tts_generator.py
import os
import config
from elevenlabs.client import ElevenLabs # Use the client interface
from elevenlabs import play, save # Helper functions

def generate_audio_from_script(script_text: str, output_filename: str):
    """
    Generates an audio file from a script with speaker labels using ElevenLabs.

    Args:
        script_text: The full text script with AGENT: and PATIENT: labels.
        output_filename: The path to save the resulting audio file (e.g., "output.mp3").

    Returns:
        True if successful, False otherwise.
    """
    if not config.ELEVENLABS_API_KEY:
        print("Error: ElevenLabs API Key is not configured in config.py or .env file.")
        return False
    if not config.AGENT_VOICE_ID or config.AGENT_VOICE_ID.startswith("YOUR_"):
        print(f"Error: AGENT_VOICE_ID is not configured correctly in config.py.")
        return False
    if not config.PATIENT_VOICE_ID or config.PATIENT_VOICE_ID.startswith("YOUR_"):
        print(f"Error: PATIENT_VOICE_ID is not configured correctly in config.py.")
        return False

    try:
        print(f"Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

        print(f"Processing script for TTS generation...")
        full_audio_segments = []
        lines = script_text.strip().split('\n')

        for line in lines:
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
                print(f"  Skipping line without speaker label: '{line}'")
                continue # Skip lines without standard labels

            if not text_to_speak:
                print(f"  Skipping empty utterance for speaker {speaker}.")
                continue

            print(f"  Generating audio for {speaker}: '{text_to_speak[:50]}...'")
            try:
                # Generate audio bytes for the current utterance
                audio_segment = client.generate(
                    text=text_to_speak,
                    voice=voice_id,
                    model=config.ELEVENLABS_MODEL
                    # You can add generation_config=GenerationConfig(...) here for more control if needed
                )
                # Check if audio_segment is valid bytes
                if isinstance(audio_segment, bytes) and len(audio_segment) > 0:
                   full_audio_segments.append(audio_segment)
                else:
                   print(f"  Warning: Received empty or invalid audio data for line: '{line}'")

            except Exception as api_e:
                print(f"  ERROR generating audio for line: '{line}'. Error: {api_e}")
                # Decide if you want to stop or continue
                # return False # Option: Stop on first error
                continue # Option: Skip failed segment and continue

        if not full_audio_segments:
             print("Error: No audio segments were successfully generated.")
             return False

        print(f"\nConcatenating {len(full_audio_segments)} audio segments...")
        # Combine the audio byte segments
        full_audio = b"".join(full_audio_segments)

        print(f"Saving combined audio to: {output_filename}...")
        save(audio=full_audio, filename=output_filename)
        print("Audio generation complete.")
        return True

    except Exception as e:
        print(f"An unexpected error occurred during TTS generation: {e}")
        return False

# --- Example Usage (Optional - Requires a sample script file) ---
# if __name__ == "__main__":
#     sample_script = f"""
# {config.AGENT_SPEAKER_LABEL}: Hello Sarah, thanks for calling.
# {config.PATIENT_SPEAKER_LABEL}: Hi Ben.
# {config.AGENT_SPEAKER_LABEL}: How can I help you today?
# {config.PATIENT_SPEAKER_LABEL}: I need to ask about my recent appointment.
# """
#     output_file = "test_tts_output.mp3"

#     if generate_audio_from_script(sample_script, output_file):
#         print(f"Successfully generated test audio: {output_file}")
#         # Optional: Play the audio if needed (requires ffplay or mpv installed)
#         # try:
#         #     print("Attempting to play generated audio...")
#         #     play(f"test_tts_output.mp3")
#         # except Exception as play_e:
#         #      print(f"Could not play audio automatically: {play_e}")
#         #      print("Please install ffplay (ffmpeg) or mpv to enable playback.")
#     else:
#         print("Failed to generate test audio.")