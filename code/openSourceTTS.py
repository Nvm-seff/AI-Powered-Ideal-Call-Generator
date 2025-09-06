# Imports (ensure these are installed locally: pip install soundfile dia-tts torch ipython) # ran on 8:06
import soundfile as sf
from dia.model import Dia
import traceback
from IPython.display import Audio # Works in Jupyter/IPython, harmless in plain script
import torch # For CUDA cache clearing
import os # For checking file existence

# Step 1: Define the transcript filename (ASSUMED TO EXIST)
TRANSCRIPT_FILENAME = "sample_transcript_ideal_call_rag.txt"

# --- Pre-run check for the transcript file ---
if not os.path.exists(TRANSCRIPT_FILENAME):
    print(f"Error: The required transcript file '{TRANSCRIPT_FILENAME}' was not found in the current directory.")
    print(f"Please make sure the file exists and contains the dialogue content.")
    # You might want to exit the script here if the file is essential
    exit()
else:
    print(f"Using existing transcript file: '{TRANSCRIPT_FILENAME}'")

# Clear CUDA cache before loading the model
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print("CUDA cache cleared before model loading.")
else:
    print("No CUDA GPU detected. Model will attempt to run on CPU (if supported by 'Dia'), which might be significantly slower.")

# --- Load and Prepare Transcript Segments ---
print(f"\nLoading transcript from: {TRANSCRIPT_FILENAME}")
model_input_parts = []
dialogue_segment_count = 0

try:
    with open(TRANSCRIPT_FILENAME, 'r', encoding='utf-8') as f:
        for line_num, line_content in enumerate(f):
            line_content = line_content.strip()
            if not line_content: continue
            # Handle potential BOM (Byte Order Mark) for UTF-8 files from Windows
            if line_num == 0 and line_content.startswith('\ufeff'):
                line_content = line_content[1:]
                if not line_content: continue

            if line_content.startswith("AGENT:"):
                text = line_content.replace("AGENT:", "", 1).strip()
                if text:
                    model_input_parts.append(f"[S1] {text}")
                    dialogue_segment_count += 1
            elif line_content.startswith("PATIENT:"):
                text = line_content.replace("PATIENT:", "", 1).strip()
                if text:
                    model_input_parts.append(f"[S2] {text}")
                    dialogue_segment_count +=1
            else:
                # Avoid printing for known non-dialogue lines like headers from the original script
                if not (line_content.startswith("**") and line_content.endswith("**")):
                    print(f"Info: Line {line_num+1} in transcript is not AGENT/PATIENT or a known header, skipping: '{line_content[:50]}...'")


    if not model_input_parts:
        print(f"Error: No valid AGENT/PATIENT lines found in {TRANSCRIPT_FILENAME}. Exiting.")
        # exit() # Or raise an error
    else:
        print(f"Processed {dialogue_segment_count} dialogue segments for model input.")
        final_model_input_text = " ".join(model_input_parts)
        print("\nFormatted text for Dia model (first 200 chars):")
        print(final_model_input_text[:200] + "...")

        print("\nLoading Dia model...")
        # You can explicitly move the model to CPU if you don't have a GPU or want to force CPU
        # device = "cuda" if torch.cuda.is_available() else "cpu"
        # model = Dia.from_pretrained("nari-labs/Dia-1.6B").to(device)
        # print(f"Model will run on {device}.")
        model = Dia.from_pretrained("nari-labs/Dia-1.6B") # Dia might handle device placement
        print("Model loaded.")
        if torch.cuda.is_available() and hasattr(model, 'parameters') and next(model.parameters(), None) is not None:
             print(f"Model is on device: {next(model.parameters()).device}")


        print("\nGenerating audio... (This may take a moment, especially on CPU)")
        output_audio_data = model.generate(final_model_input_text)
        print("Audio generated.")

        OUTPUT_FILENAME = "dialogue_output.mp3"
        SAMPLE_RATE = 44100 # Dia model default is 44.1kHz
        sf.write(OUTPUT_FILENAME, output_audio_data, SAMPLE_RATE)
        print(f"\nAudio saved as {OUTPUT_FILENAME}")

except FileNotFoundError:
    # This specific error is less likely now with the os.path.exists check, but good to keep.
    print(f"Error: Transcript file not found at {TRANSCRIPT_FILENAME}.")
except torch.cuda.OutOfMemoryError as e:
    print(f"CUDA Out of Memory Error: {e}")
    print("Try restarting the kernel/script and running again. If it persists, the model might be too large for the available GPU memory.")
    if torch.cuda.is_available():
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"Total GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        print(f"Allocated GPU Memory: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
        print(f"Cached GPU Memory: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
except ImportError as e:
    print(f"ImportError: {e}. Please ensure all required libraries are installed.")
    print("You might need to run: pip install soundfile dia-tts torch torchaudio torchvision ipython")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    traceback.print_exc()

finally:
    # Attempt to free memory after use (or if an error occurs)
    if 'model' in locals() or 'model' in globals(): # Check both local and global scope
        del model
        print("Model deleted from memory.")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("CUDA cache cleared at the end.")
    else:
        print("No CUDA GPU was used or available for final cache clearing.")