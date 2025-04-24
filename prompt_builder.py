# prompt_builder.py
from typing import List
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

# --- Example Usage (Optional) ---
# if __name__ == "__main__":
#     from kpis import KPI_LIST # Assuming kpis.py is in the same directory
#     sample_transcript = "AGENT: Hello, Clinic X. My name is Bob.\nPATIENT: Hi, I need help.\nAGENT: Okay what's name?\nPATIENT: Jane Doe.\nAGENT: Okay Jane what's wrong?"
#     generated_prompt = build_analysis_prompt(sample_transcript, KPI_LIST)
#     print("\n--- Generated Prompt ---")
#     print(generated_prompt)