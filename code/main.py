# main.py
import json
import os
import code.config as config # To access configuration constants easily if needed
from code.kpis import KPI_LIST
from typing import List, Dict, Any
from code.transcript_processor import load_transcript
# Import BOTH prompt builders now
from code.prompt_builder import build_analysis_prompt, build_ideal_call_prompt
from code.gemini_client import generate_analysis # This function handles sending prompts to Gemini
from code.analysis_parser import parse_gemini_response
from code.retriever import retrieve_relevant_knowledge
from tts_generator import generate_audio_from_script # <-- Import the TTS function

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


def generate_and_display_ideal_call(original_transcript: str, analysis_result: Dict[str, Any], transcript_file_path: str):
    """
    Generates and displays/saves the ideal call text using RAG.

    Args:
        original_transcript: The original call transcript text.
        analysis_result: The parsed analysis report dictionary.
        transcript_file_path: Original transcript path used for naming output file.
    """
    print(f"\n--- Starting Ideal Call Generation (RAG Workflow) ---")

    # --- RAG Step 1: Retrieval ---
    print("Retrieving relevant knowledge based on analysis...")
    retrieved_knowledge_chunks = retrieve_relevant_knowledge(analysis_result)
    # print("\nRetrieved Knowledge for Prompt:") # Optional: print retrieved chunks
    # for chunk in retrieved_knowledge_chunks:
    #     print(chunk)

    # --- RAG Step 2: Augmentation & Prompt Building ---
    print("\nBuilding RAG prompt for ideal call generation...")
    ideal_call_prompt = build_ideal_call_prompt(
        original_transcript,
        analysis_result,
        retrieved_knowledge_chunks # Pass the retrieved chunks here
    )
    # print("\n--- Ideal Call RAG Prompt Snippet ---") # Optional: Debug prompt
    # print(ideal_call_prompt[:1000] + "...")

    # --- RAG Step 3: Generation ---
    print("\nGenerating ideal call using Gemini with retrieved knowledge...")
    ideal_call_text = generate_analysis(ideal_call_prompt) # Reuse the Gemini client function

    # --- Handle Generation Output ---
    if ideal_call_text:
        print("\n--- Ideal Call Generation Successful ---")
        print("\n**Generated Ideal Call Suggestions (using RAG):**\n")
        print(ideal_call_text)

        # Save the result to a file
        output_filename = transcript_file_path.replace(".txt", "_ideal_call_rag.txt") # New name
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(ideal_call_text)
            print(f"\nIdeal call suggestions saved to: {output_filename}")

            # --- Generate Audio ---
            #audio_output_filename = transcript_file_path.replace(".txt", "_ideal_call_audio.mp3")
            #print("\n--- Starting Audio Generation ---")
            #if generate_audio_from_script(ideal_call_text, audio_output_filename):
            #     print(f"Ideal call audio successfully generated and saved to: {audio_output_filename}")
            #else:
            #     print(f"Ideal call audio generation failed.")
            # --- End Audio Generation ---
            
        except Exception as e:
            print(f"Error saving ideal call suggestions: {e}")

    else:
        print("\n--- Ideal Call Generation Failed ---")
        print("Failed to get ideal call response from Gemini (RAG).")

    


def generate_dummy_transcript(transcript_to_process:str):
        # --- Ensure sample transcript exists for testing ---
    if not os.path.exists(transcript_to_process):
         print(f"Creating dummy transcript file: {transcript_to_process}")
         with open(transcript_to_process, "w", encoding='utf-8') as f:
            f.write(f"{config.AGENT_SPEAKER_LABEL}: Hello, thank you for calling Healthy Clinic, my name is Ben. May I start with your full name, please?\n")
            # KPI Met: Introduction

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Hi Ben, it's Sarah Miller.\n")
            # KPI Met: Got Name

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay Sarah, thanks. Could you spell your last name for me?\n")
            # KPI Met: Verify Spelling

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Sure, M-I-L-L-E-R.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Got it. And what's the best phone number to reach you?\n")
            # KPI Met: Verify Phone Number

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: 555-987-6543.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, 555-987-6543. So, what brings you in today?\n")
            # KPI Missed: Capture Lead Source.
            # Soft Skill Note: Transition is okay, not particularly warm or engaging.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: My left shoulder has been really stiff and painful for about two weeks.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Your left shoulder, okay. Besides stiff and painful, are there any other symptoms like clicking, grinding, or weakness?\n")
            # KPI Met: Detailed description (affected body part).
            # KPI Met: Asking about symptoms.
            # Soft Skill Note: Good clarifying question.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: It's mainly the stiffness, and I definitely feel weaker when I try to lift things overhead.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: And this started about two weeks ago? Has it been constant, or does it come and go?\n")
            # KPI Met: Duration / Recurrence pattern.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: It's been pretty constant since it started.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Alright. Is this related to any specific injury, like a fall, car accident, or anything at work?\n")
            # KPI Met: Identify if MVA/WC/Legal related.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: No, not that I can think of. It just kind of started.\n")
            # Note: Accident-related KPIs should now be N/A based on this answer.

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Have you had any prior treatment or seen any other doctors for this specific shoulder issue before?\n")
            # KPI Met: Ask about previous treatments.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: No, this is the first time.\n")
            # Note: Previous treatment detail KPIs (providers, contacts, procedures, tests, records) should be N/A.

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay. Let's look at insurance. Do you have health insurance you'd like to use?\n")
            # Soft Skill Note: Functional transition, slightly abrupt.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Yes, I have Aetna.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, Aetna. Could I get the Member ID number from your card?\n")
            # KPI Met: Ask for Insurance ID.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: It's W123456789.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: W123456789. Is there a group number as well?\n")
            # KPI Met: Ask for Insurance Group.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Yes, GRP-ABC.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: And are you the subscriber, the main person on the policy?\n")
            # KPI Met: Ask for Insurance Subscriber relationship.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Yes.\n")
            # Note: Subscriber Name/DOB KPIs should be N/A.

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Do you have any secondary insurance coverage?\n")
            # KPI Met: Ask about Secondary Insurer.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: No, just the Aetna.\n")

            # --- Potential Miss #2 ---
            # KPI Missed: Disclose Out-of-Network status (Assuming this is required)
            # Agent proceeds directly to scheduling without mentioning network status.

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Okay, thanks for that information. Let me check the schedule... It looks like Dr. Davis has an opening this Friday at 10:30 AM. Would that time work for you?\n")
            # Note: Appointment offered.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Yes, Friday at 10:30 is perfect.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Great. So that's booked. Friday at 10:30 AM with Dr. Davis at our main clinic on 456 Health Drive. We'll send you a text message with a link to our online new patient portal to complete your paperwork beforehand. Please try to do that at least a day before your visit.\n")
            # KPI Met: Confirm Appointment Date.
            # KPI Met: Confirm Appointment Time.
            # KPI Met: Confirm Provider.
            # KPI Met: Confirm Location.
            # KPI Met: Reiterate Next Steps (Packet/Portal).

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Okay, sounds good.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Do you have any other questions right now?\n")
            # Soft Skill Note: Good practice to ask for questions.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: No, thank you.\n")

            f.write(f"{config.AGENT_SPEAKER_LABEL}: Alright then, Sarah. We look forward to seeing you on Friday. Have a good day!\n")
            # Soft Skill Note: Standard, polite closing. Confidence/Energy likely average.

            f.write(f"{config.PATIENT_SPEAKER_LABEL}: Thanks, you too. Bye.\n")
    
    print(f"File {transcript_to_process} created.")

if __name__ == "__main__":
    # --- INPUT: Specify the path to your transcript file ---
    transcript_to_process = "sample_transcript1.txt" # <--- CHANGE THIS

    if not os.path.exists("sample_transcript1.txt"):
        generate_dummy_transcript(transcript_to_process)


 # --- Ensure knowledge base dir and some files exist ---
    KB_DIRECTORY = "knowledge_base" # Make sure this matches retriever.py
    if not os.path.exists(KB_DIRECTORY):
        os.makedirs(KB_DIRECTORY)
        print(f"Created directory: {KB_DIRECTORY}")
    knowledge_files_to_check = ["sop_introduction.txt", "sop_verification.txt", "examples_empathy.txt"]
    for fname in knowledge_files_to_check:
        fpath = os.path.join(KB_DIRECTORY, fname)
        if not os.path.exists(fpath):   # Just Checking here k if Knowledge base not made then insert random shi there 
            print(f"Creating dummy knowledge file: {fpath}")
            content = f"Content for {fname}. Example: keyword {fname.split('.')[0].split('_')[-1]}"
            with open(fpath, "w") as f:
                f.write(content)


    # --- STEP 1: Run Analysis ---
    analysis_data = run_analysis(transcript_to_process)

    # --- STEP 2: Generate Ideal Call Text & Audio (if analysis was successful) ---
    if analysis_data:
        original_transcript_content = load_transcript(transcript_to_process)
        if original_transcript_content:
             generate_and_display_ideal_call(original_transcript_content, analysis_data, transcript_to_process)
        else:
            print("Could not reload transcript to generate ideal call.")
    else:
        print("\nSkipping ideal call generation because analysis failed or was not performed.")

    print("\n--- Script Finished ---")