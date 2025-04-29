# prompt_builder.py
from typing import List, Dict, Any
import config # Import config to get speaker labels

def build_analysis_prompt(transcript: str, kpis: List[str]) -> str:
    """
    Builds the prompt for Gemini analysis, incorporating transcript and KPIs.

    Args:
        transcript: The full call transcript string (with speaker labels).
        kpis: A list of KPI questions.

    Returns:
        The formatted prompt string ready for the Gemini API.
    """
    kpi_string = "\n".join([f"- {kpi}" for kpi in kpis])

    # Instructions clearly stating the agent and patient labels from config
    prompt = f"""
    **Objective:** Analyze the performance of the customer support representative ('{config.AGENT_SPEAKER_LABEL}') in the following patient call transcript ('{config.PATIENT_SPEAKER_LABEL}'). Evaluate adherence to KPIs, identify mistakes, and assess communication skills.

    **Call Transcript:**
    ```
    {transcript}
    ```

    **Instructions:**

    1.  **KPI Analysis:** Review the transcript *specifically* focusing on the actions and dialogue of the '{config.AGENT_SPEAKER_LABEL}'. For each KPI listed below, determine if it was 'Met', 'Not Met', or 'Not Applicable' (N/A) based *only* on the provided transcript. Provide a concise justification, especially for 'Not Met' or 'N/A'.
    2.  **Mistake Identification & Improvement Areas:** Identify specific mistakes made by the '{config.AGENT_SPEAKER_LABEL}' or areas needing improvement. Consider missed information, incorrect statements, poor communication style (tone, empathy, clarity, flow), lack of confidence, failure to follow procedures (like disclosures), etc. Reference specific phrases from the transcript if possible.
    3.  **Soft Skills Evaluation:** Assess the '{config.AGENT_SPEAKER_LABEL}'s' soft skills based on the interaction.
    4.  **Output Format:** Structure your entire response *strictly* as a single JSON object. Do not include any text before or after the JSON object.

    **KPI Checklist:**
    {kpi_string}

    **Requested JSON Output Structure:**
    ```json
    {{
      "kpi_analysis": [
        {{
          "kpi": "KPI text (e.g., Did the representative introduce themselves?)",
          "status": "Met | Not Met | N/A",
          "reason": "Brief justification based on the agent's dialogue in the transcript."
        }}
        // ... include one entry for each KPI from the list above
      ],
      "overall_assessment": {{
        "summary": "A brief overall summary of the agent's performance.",
        "strengths": [
            "List key strengths observed in the agent's performance (e.g., 'Clear introduction', 'Empathetic tone during symptom description')."
        ],
        "mistakes_and_improvement_areas": [
            "Specific mistake or area 1 (e.g., 'Failed to verify phone number after obtaining name.')",
            "Specific mistake or area 2 (e.g., 'Tone sounded rushed when discussing previous treatments.')"
          // ... list all significant points
        ],
        "soft_skills_evaluation": {{
           "confidence": "Assessment (e.g., Confident, Hesitant, Average, Overconfident)",
           "positivity_tone": "Assessment (e.g., Consistently Positive, Neutral, Mostly Negative, Fluctuated)",
           "energy_level": "Assessment (e.g., Consistent, High, Low, Variable)",
           "enthusiasm": "Assessment (e.g., Enthusiastic, Neutral, Lacking, Forced)",
           "empathy_relatability": "Assessment (e.g., Highly Empathetic, Showed Some Empathy, Neutral, Lacked Empathy)",
           "conversation_steering": "Assessment (e.g., Effectively Guided Conversation, Lost Control at Times, Followed Patient Too Much, Rigidly Scripted)",
           "genuineness": "Assessment (e.g., Sounded Genuine, Sounded Scripted, Rushed)",
           "conversation_flow": "Assessment (e.g., Smooth and Natural, Some Awkward Pauses, Frequent Dead Space)"
        }}
      }}
    }}
    ```
    """
    return prompt


# --- NEW Function ---
def build_ideal_call_prompt(original_transcript: str, analysis_report: Dict[str, Any], retrieved_knowledge: List[str]) -> str:
    """
    Builds the prompt for Gemini to generate an ideal call script,
    augmented with retrieved knowledge based on the analysis report.

    Args:
        original_transcript: The full original call transcript string.
        analysis_report: The parsed JSON analysis report as a dictionary.
        retrieved_knowledge: A list of strings containing relevant knowledge chunks.

    Returns:
        The formatted RAG prompt string for ideal call generation.
    """
    missed_kpis = [item['kpi'] for item in analysis_report.get('kpi_analysis', []) if item.get('status') == 'Not Met']
    improvement_areas = analysis_report.get('overall_assessment', {}).get('mistakes_and_improvement_areas', [])

    missed_kpis_string = "\n".join([f"- {kpi}" for kpi in missed_kpis]) if missed_kpis else "None identified."
    improvement_areas_string = "\n".join([f"- {area}" for area in improvement_areas]) if improvement_areas else "None identified."

    # Format the retrieved knowledge for inclusion in the prompt
    retrieved_knowledge_string = "\n\n".join(retrieved_knowledge) if retrieved_knowledge else "No specific knowledge chunks were retrieved for this task."

    prompt = f"""
    **Objective:** Generate an improved version or specific improved segments of a patient call script for the customer support representative ('{config.AGENT_SPEAKER_LABEL}'). This generated script should serve as a training example, addressing the weaknesses identified in the original call analysis **by incorporating the provided best practices and examples.**

    **Original Call Transcript:**
    ```
    {original_transcript}
    ```

    **Analysis Summary (Weaknesses Identified):**

    *   **Missed KPIs:**
    {missed_kpis_string}

    *   **Specific Mistakes / Areas for Improvement:**
    {improvement_areas_string}

    **Retrieved Knowledge (Best Practices / Examples):**
    {retrieved_knowledge_string}

    **Task:**

    1.  **Rewrite Agent Dialogue:** Focus on rewriting the dialogue for '{config.AGENT_SPEAKER_LABEL}'. Incorporate best practices to address the 'Missed KPIs' and 'Mistakes/Improvement Areas' listed above. **Crucially, use the guidance and examples provided in the 'Retrieved Knowledge' section** to inform the phrasing, questions asked, and overall approach. Ensure all necessary information according to the KPIs is gathered correctly and sensitively.
    2.  **Demonstrate Soft Skills:** The rewritten dialogue should demonstrate positive tone, confidence, empathy, clarity, and effective conversation control, referencing the retrieved knowledge where applicable (e.g., for empathetic statements).
    3.  **Maintain Context:** Keep the '{config.PATIENT_SPEAKER_LABEL}'s dialogue mostly the same as the original transcript to show how the agent *should have* responded. Minor adjustments are acceptable for flow.
    4.  **Format:** Present the output as a revised script or script segments. Clearly label the speakers using '{config.AGENT_SPEAKER_LABEL}:' and '{config.PATIENT_SPEAKER_LABEL}:'. Focus on the most critical segments needing improvement, guided by the analysis and retrieved knowledge. *Do not* output JSON.

    **Generate the improved script/segments now, using the provided knowledge:**
    """
    return prompt
# --- Example Usage (Optional) ---
# if __name__ == "__main__":
#     # Assume sample_transcript.txt exists from previous steps
#     # Assume sample_transcript_analysis.json exists and is valid
#     import os
#     from transcript_processor import load_transcript
#     import json

#     sample_transcript_file = "sample_transcript.txt"
#     sample_analysis_file = "sample_transcript_analysis.json" # Assume generated by previous run

#     if os.path.exists(sample_transcript_file) and os.path.exists(sample_analysis_file):
#         original_transcript = load_transcript(sample_transcript_file)
#         try:
#             with open(sample_analysis_file, 'r', encoding='utf-8') as f:
#                 analysis_data = json.load(f)

#             if original_transcript and analysis_data:
#                 ideal_call_prompt = build_ideal_call_prompt(original_transcript, analysis_data)
#                 print("\n--- Generated Ideal Call Prompt ---")
#                 print(ideal_call_prompt)
#             else:
#                 print("Error loading transcript or analysis data.")
#         except Exception as e:
#             print(f"Error reading or parsing analysis file {sample_analysis_file}: {e}")
#     else:
#         print(f"Error: Ensure both {sample_transcript_file} and {sample_analysis_file} exist.")