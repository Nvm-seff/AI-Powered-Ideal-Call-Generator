# main.py
import json
import config # To access configuration constants easily if needed
from kpis import KPI_LIST
from transcript_processor import load_transcript
from prompt_builder import build_analysis_prompt
from gemini_client import generate_analysis
from analysis_parser import parse_gemini_response

def run_analysis(transcript_file_path: str):
    """
    Runs the full call analysis pipeline.

    Args:
        transcript_file_path: Path to the call transcript file.
    """
    print(f"--- Starting Analysis for: {transcript_file_path} ---")

    # 1. Load Transcript
    transcript = load_transcript(transcript_file_path)
    if not transcript:
        print("Analysis aborted: Could not load transcript.")
        return

    # (Optional) Print snippet of transcript
    # print("\n--- Transcript Snippet ---")
    # print(transcript[:500] + "...")
    # print("-" * 20)

    # 2. Build Prompt
    print("Building analysis prompt...")
    prompt = build_analysis_prompt(transcript, KPI_LIST)
    # (Optional) Print snippet of prompt
    # print("\n--- Prompt Snippet ---")
    # print(prompt[:500] + "...")
    # print("-" * 20)


    # 3. Get Analysis from Gemini
    raw_analysis_response = generate_analysis(prompt)
    if not raw_analysis_response:
        print("Analysis aborted: Failed to get response from Gemini.")
        return

    # 4. Parse the Response
    analysis_result = parse_gemini_response(raw_analysis_response)

    # 5. Display/Save Results
    if analysis_result:
        print("\n--- Analysis Successful ---")
        # Pretty print the JSON analysis
        print(json.dumps(analysis_result, indent=2))

        # TODO: Save the result to a file or database if needed
        output_filename = transcript_file_path.replace(".txt", "_analysis.json")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"\nAnalysis saved to: {output_filename}")
        except Exception as e:
            print(f"Error saving analysis results: {e}")

    else:
        print("\n--- Analysis Failed ---")
        print("Could not parse a valid JSON object from the Gemini response.")
        # The parser function already printed the raw response for debugging

    print(f"--- Analysis Finished for: {transcript_file_path} ---")


if __name__ == "__main__":
    # --- INPUT: Specify the path to your transcript file ---
    # Ensure this file exists and contains the diarized transcript
    # with speaker labels matching those in config.py (e.g., AGENT:, PATIENT:)
    transcript_to_analyze = "sample_transcript.txt" # <--- CHANGE THIS

    # Create a dummy sample file if it doesn't exist for a quick test
    import os
    if not os.path.exists(transcript_to_analyze):
         print(f"Creating dummy transcript file: {transcript_to_analyze}")
         with open(transcript_to_analyze, "w", encoding='utf-8') as f:
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Hello, thank you for calling Healthy Clinic, my name is Alex. May I have your full name, please?\n")
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Yes, it's Jane Doe.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Thanks, Jane. Could you spell that for me?\n")
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: J-A-N-E D-O-E.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Perfect, thank you. And Jane, what is the primary reason for your call today?\n") # Missed phone verification, lead source
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: My knee has been really painful for the last week.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, the knee. Is it your right or left?\n") # Good specification
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: The left one.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Got it. Have you had any treatment for this before?\n") # Asking about previous treatment
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: No, not for this.\n")


    run_analysis(transcript_to_analyze)