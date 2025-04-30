from elevenlabs.client import ElevenLabs
import os
import config

client = ElevenLabs(
    api_key=config.ELEVENLABS_API_KEY
)

audio_stream = client.text_to_speech.convert(
    voice_id="21m00Tcm4TlvDq8ikWAM",  # "Rachel"
    model_id="eleven_monolingual_v1",
    text="Hello, this is a test."
)

# Save streamed audio to a file
with open("output.wav", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)