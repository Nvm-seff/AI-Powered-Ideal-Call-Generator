# main.py
import json
import os
import config # To access configuration constants easily if needed
from kpis import KPI_LIST
from typing import List, Dict, Any
from transcript_processor import load_transcript
# Import BOTH prompt builders now
from prompt_builder import build_analysis_prompt, build_ideal_call_prompt
from gemini_client import generate_analysis # This function handles sending prompts to Gemini
from analysis_parser import parse_gemini_response

def run_analysis(transcript_file_path: str) -> Dict[str, Any] | None:
    """
    Runs the call analysis pipeline and returns the parsed analysis report.

    Args:
        transcript_file_path: Path to the call transcript file.

    Returns:
        The parsed analysis report as a dictionary, or None if analysis fails.
    """
    print(f"\n--- Starting Analysis for: {transcript_file_path} ---")

    # 1. Load Transcript
    transcript = load_transcript(transcript_file_path)
    if not transcript:
        print("Analysis aborted: Could not load transcript.")
        return None

    # 2. Build Analysis Prompt
    print("Building analysis prompt...")
    analysis_prompt = build_analysis_prompt(transcript, KPI_LIST)

    # 3. Get Analysis from Gemini
    raw_analysis_response = generate_analysis(analysis_prompt)
    if not raw_analysis_response:
        print("Analysis aborted: Failed to get analysis response from Gemini.")
        return None

    # 4. Parse the Analysis Response
    analysis_result = parse_gemini_response(raw_analysis_response)

    # 5. Display/Save Analysis Results
    if analysis_result:
        print("\n--- Analysis Successful ---")
        # print(json.dumps(analysis_result, indent=2)) # Keep console clean, save to file

        # Save the result to a file
        output_filename = transcript_file_path.replace(".txt", "_analysis.json")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to: {output_filename}")
            return analysis_result # Return the parsed result
        except Exception as e:
            print(f"Error saving analysis results: {e}")
            return None # Failed to save, treat as failure

    else:
        print("\n--- Analysis Failed ---")
        print("Could not parse a valid JSON object from the Gemini analysis response.")
        return None

# --- NEW Function ---
def generate_and_display_ideal_call(original_transcript: str, analysis_result: Dict[str, Any], transcript_file_path: str):
    """
    Generates and displays/saves the ideal call text based on analysis.

    Args:
        original_transcript: The original call transcript text.
        analysis_result: The parsed analysis report dictionary.
        transcript_file_path: Original transcript path used for naming output file.
    """
    print(f"\n--- Starting Ideal Call Generation based on Analysis ---")

    # 1. Build Ideal Call Prompt
    print("Building ideal call prompt...")
    ideal_call_prompt = build_ideal_call_prompt(original_transcript, analysis_result)

    # 2. Get Ideal Call Text from Gemini
    # We re-use the generic 'generate_analysis' function from gemini_client
    # Note: Consider adjusting temperature via GenerationConfig if needed for this specific task
    ideal_call_text = generate_analysis(ideal_call_prompt)

    # 3. Display/Save Ideal Call Text
    if ideal_call_text:
        print("\n--- Ideal Call Generation Successful ---")
        print("\n**Generated Ideal Call Suggestions:**\n")
        print(ideal_call_text)

        # Save the result to a file
        output_filename = transcript_file_path.replace(".txt", "_ideal_call.txt")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(ideal_call_text)
            print(f"\nIdeal call suggestions saved to: {output_filename}")
        except Exception as e:
            print(f"Error saving ideal call suggestions: {e}")

    else:
        print("\n--- Ideal Call Generation Failed ---")
        print("Failed to get ideal call response from Gemini.")


if __name__ == "__main__":
    # --- INPUT: Specify the path to your transcript file ---
    transcript_to_process = "sample_transcript.txt" # <--- CHANGE THIS

    # --- Ensure sample transcript exists for testing ---
    if not os.path.exists(transcript_to_process):
         print(f"Creating dummy transcript file: {transcript_to_process}")
         with open(transcript_to_process, "w", encoding='utf-8') as f:
            # Simple example with obvious omissions for testing
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Clinic, hello.\n") # Bad intro
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Hi, I need to see someone about my back.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, name?\n") # Missing verification, spelling, phone
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: John Smith.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: And what's the problem with the back?\n") # Vague
            f.write(f"{config.PATIENT_SPEAKER_LABEL}: It just really hurts when I bend over.\n")
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, we can see you Tuesday at 10.\n") # Missed many KPIs

    # --- STEP 1: Run Analysis ---
    analysis_data = run_analysis(transcript_to_process)

    # --- STEP 2: Generate Ideal Call (if analysis was successful) ---
    if analysis_data:
        # Need the original transcript again for the ideal call prompt
        original_transcript_content = load_transcript(transcript_to_process)
        if original_transcript_content:
             generate_and_display_ideal_call(original_transcript_content, analysis_data, transcript_to_process)
        else:
            print("Could not reload transcript to generate ideal call.")
    else:
        print("\nSkipping ideal call generation because analysis failed or was not performed.")

    print("\n--- Script Finished ---")