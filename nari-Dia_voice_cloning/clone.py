import os
from dia.model import Dia


model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")

from dia.model import Dia


model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")

# You should put the transcript of the voice you want to clone
# We will use the audio created by running simple.py as an example.
# Note that you will be REQUIRED TO RUN simple.py for the script to work as-is.
# --- Configuration using os.path.join ---
BASE_DIR = "../voice_samples"

clone_from_text = ""
# Load transcript from text file
transcript_path = os.path.join(BASE_DIR, "sample_transcript_for_cloning.txt")
with open(transcript_path, "r", encoding="utf-8") as f:
    clone_from_text = f.read()

# Load audio path
clone_from_audio = os.path.join(BASE_DIR, "sample_output_for_cloning.mp3")

# For your custom needs, replace above with below and add your audio file to this directory:
# clone_from_text = "[S1] ... [S2] ... [S1] ... corresponding to your_audio_name.mp3"
# clone_from_audio = "your_audio_name.mp3"

# Text to generate
text_to_generate = ""

with open("sample_transcript.txt", "r", encoding="utf-8") as f:
    text_to_generate = f.read()

print(text_to_generate)

input("Press Enter to continue...")

# It will only return the audio from the text_to_generate
output = model.generate(
    clone_from_text + text_to_generate, audio_prompt=clone_from_audio, use_torch_compile=False, verbose=True
)

model.save_audio("voice_clone.mp3", output)
# For your custom needs, replace above with below and add your audio file to this directory:
# clone_from_text = "[S1] ... [S2] ... [S1] ... corresponding to your_audio_name.mp3"
# clone_from_audio = "your_audio_name.mp3"