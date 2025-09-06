# transcript_processor.py
import os

def load_transcript(file_path: str) -> str | None:
    """
    Loads the transcript content from a text file.

    Args:
        file_path: The path to the transcript file.

    Returns:
        The content of the transcript as a single string,
        or None if the file cannot be read.
    """
    if not os.path.exists(file_path):
        print(f"Error: Transcript file not found at {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        print(f"Successfully loaded transcript from: {file_path}")
        return transcript_content
    except Exception as e:
        print(f"Error reading transcript file {file_path}: {e}")
        return None

# --- Example Usage (Optional) ---
# if __name__ == "__main__":
#     sample_file = "sample_transcript.txt" # Make sure this file exists for testing
#     # Create a dummy sample file for testing
#     if not os.path.exists(sample_file):
#         with open(sample_file, "w") as f:
#             f.write("AGENT: Hello, thank you for calling Clinic X, my name is Alex. Can I get your name please?\n")
#             f.write("PATIENT: Hi Alex, my name is Jane Doe.\n")
#             f.write("AGENT: Okay Jane, could you spell that for me?\n")
#             f.write("PATIENT: J-A-N-E D-O-E.\n")
#             f.write("AGENT: Got it. And what's bothering you today?\n") # Missed phone verification etc.
#             f.write("PATIENT: My lower back hurts a lot.\n")
#
#     content = load_transcript(sample_file)
#     if content:
#         print("\n--- Transcript Content ---")
#         print(content)