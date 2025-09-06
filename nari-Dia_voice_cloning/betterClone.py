import os
import re
import numpy as np
import soundfile as sf
from dia.model import Dia
import torch

# --- Configuration ---
print("Loading Dia model...")
model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
print("Model loaded.")

# --- Paths and Original Cloning Source ---
BASE_DIR_SAMPLES = "../voice_samples"
clone_from_text_path = os.path.join(BASE_DIR_SAMPLES, "sample_transcript_for_cloning.txt")
clone_from_audio_path = os.path.join(BASE_DIR_SAMPLES, "sample_output_for_cloning.mp3")

try:
    with open(clone_from_text_path, "r", encoding="utf-8") as f:
        prompt_voice_transcript = f.read().strip()
    print(f"Loaded cloning prompt transcript: '{prompt_voice_transcript[:100]}...'")
except FileNotFoundError:
    print(f"ERROR: Cloning transcript file not found at {clone_from_text_path}")
    exit()

if not os.path.exists(clone_from_audio_path):
    print(f"ERROR: Cloning audio file not found at {clone_from_audio_path}")
    exit()
print(f"Using cloning audio: {clone_from_audio_path}")

# --- Full Conversation Transcript (Text to Generate in Chunks) ---
full_conversation_to_generate_path = "sample_transcript.txt"
try:
    with open(full_conversation_to_generate_path, "r", encoding="utf-8") as f:
        full_conversation_script = f.read()
    print(f"Loaded full conversation script from '{full_conversation_to_generate_path}'.")
except FileNotFoundError:
    print(f"ERROR: Conversation script file ('{full_conversation_to_generate_path}') not found.")
    exit()

# --- Modified Function to parse transcript into S1-S2 pairs ---
def parse_transcript_into_s1_s2_pairs(transcript_text):
    # First, get all individual turns (S1 or S2)
    individual_turns = []
    # Regex to find [S1] or [S2] tags and the text following them, including their original tags
    raw_matches = re.finditer(r"(\[S[12]\]\s*.*?(?=\n\[S[12]\]|$))", transcript_text, re.DOTALL)
    for match in raw_matches:
        full_turn_text = match.group(1).strip() # Includes the [S_] tag
        if full_turn_text:
            individual_turns.append(full_turn_text)

    s1_s2_pairs = []
    i = 0
    while i < len(individual_turns):
        current_turn = individual_turns[i]
        if current_turn.startswith("[S1]"):
            pair_text = current_turn
            # Check if the next turn exists and is an S2
            if (i + 1) < len(individual_turns) and individual_turns[i+1].startswith("[S2]"):
                pair_text += "\n" + individual_turns[i+1]
                pair_text += "\n[S1] "
                i += 1 # Increment to skip the S2 turn in the next iteration
            else :
                pair_text +="\n[S2] "
            # Add the pair (or solo S1 if no S2 followed)
            # We need the text content without the tags for TTS, but preserve tags for context
            s1_s2_pairs.append(pair_text)
        elif current_turn.startswith("[S2]"):
            # Handle orphaned S2 if necessary, or just skip them if we only start pairs with S1
            # For now, let's assume S2s are only processed if they follow an S1.
            # If an S2 appears first or alone, it won't form a pair with this logic.
            # Alternatively, you could add solo S2s too:
            # s1_s2_pairs.append({"speaker_info": "S2_SOLO", "text_segment_for_tts": current_turn.replace("[S2]", "").strip()})
            pass
        i += 1
    return s1_s2_pairs

parsed_dialogue_chunks = parse_transcript_into_s1_s2_pairs(full_conversation_script)

if not parsed_dialogue_chunks:
    print("ERROR: No S1-S2 pairs or S1 turns found in the conversation script.")
    exit()

print(f"\nParsed {len(parsed_dialogue_chunks)} S1-S2 conversational chunks.")
for i, chunk in enumerate(parsed_dialogue_chunks[:2]): # Print first 2 chunks
    print(f"  Chunk {i+1}:\n{chunk}\n--------------------")



# --- Iterative Generation for each S1-S2 chunk ---
all_audio_clips = []
sample_rate = 44100

print("\nStarting chunked audio generation for S1-S2 pairs...")

for i, text_chunk_to_generate in enumerate(parsed_dialogue_chunks):
    # The text_chunk_to_generate already includes [S1] and [S2] tags.
    # The TTS model might interpret these tags or ignore them.
    # For Dia, it's often better to provide clean text without speaker tags for the actual synthesis part.
    # However, the model was trained on data that might have had such tags.
    # Let's first try sending the text with tags, as it preserves speaker turn info.
    # If the model speaks the "[S1]" tags out loud, we'll need to strip them before sending to TTS.

    # For TTS, we typically want the text *without* the [S1]/[S2] speaker markers being spoken.
    # The structure of the text (S1 line, newline, S2 line) implies the turns.
    # Let's prepare a "cleaner" version for TTS if needed, but pass the tagged one first.
    # The Dia model might use [S1] as a cue for the prompter's voice.

    # The text for `model.generate` should be `prompt_voice_transcript` + `text_chunk_to_generate`
    # And the output is assumed to be *only* for `text_chunk_to_generate`.

    print(f"  Generating audio for chunk {i+1}/{len(parsed_dialogue_chunks)}:\n'{text_chunk_to_generate[:150]}...'")
    
    # Construct the input text for the model
    # The `prompt_voice_transcript` is the transcript of your `clone_from_audio_path`
    # `text_chunk_to_generate` is the S1/S2 pair.
    text_for_model_input = prompt_voice_transcript + "\n" + text_chunk_to_generate
    # Using newline as a separator, could also be a space.

    try:
        raw_output = model.generate(
            text=text_for_model_input,
            audio_prompt=clone_from_audio_path,
            use_torch_compile=False,
            verbose=False
        )

        processed_np_output = np.array([], dtype=np.float32)

        if raw_output is not None:
            if isinstance(raw_output, torch.Tensor):
                if raw_output.nelement() > 0:
                    processed_np_output = raw_output.cpu().numpy().flatten()
            elif isinstance(raw_output, np.ndarray):
                if raw_output.size > 0:
                    processed_np_output = raw_output.flatten()

        if processed_np_output.size > 0:
            all_audio_clips.append(processed_np_output)
            print(f"  Chunk {i+1} generated successfully (samples: {len(processed_np_output)}).")
        else:
            print(f"  Warning: Chunk {i+1} - No audio data or empty audio generated.")
            all_audio_clips.append(np.array([], dtype=np.float32))

    except Exception as e:
        print(f"  ERROR generating audio for chunk {i+1}:")
        print(f"  Text: '{text_chunk_to_generate[:60]}...'")
        print(f"  Error details: {e}")
        all_audio_clips.append(np.array([], dtype=np.float32))

print("All chunks processed.")

# --- Concatenate All Generated Audio Clips ---
if any(clip.size > 0 for clip in all_audio_clips):
    final_concatenated_audio = np.concatenate([clip for clip in all_audio_clips if clip.size > 0])

    output_filename = "cloned_voice_s1_s2_pairs_conversation.wav"
    try:
        sf.write(output_filename, final_concatenated_audio, samplerate=sample_rate)
        print(f"\nFinal concatenated audio saved to: {output_filename} (Sample rate: {sample_rate})")
    except Exception as e:
        print(f"Error saving concatenated audio: {e}")
        print("Make sure you have 'soundfile' and 'numpy' installed: pip install soundfile numpy")
else:
    print("No audio clips were successfully generated to concatenate.")

print("\nScript finished.")