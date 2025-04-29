import os

# Define the directory where knowledge base files will be stored
KB_DIRECTORY = "knowledge_base"

# Define the content for each knowledge base file
# Using triple quotes for multi-line strings
knowledge_content = {
    "sop_introduction.txt": """
Best Practice: Start calls professionally and clearly state your name and the clinic's name. Aim to immediately engage the patient politely.

Example Script Opening:
'Thank you for calling CareCloud MTBC , my name is [Agent Name]. To help you best today, could I please start with your full name?'

Key elements:
- Greeting (Thank you for calling...)
- Clinic Name
- Agent Name
- Polite request for patient identification (e.g., name)
""",

    "sop_verification.txt": """
Best Practice: Verify essential contact and identifying information early in the call, typically right after obtaining the patient's name. This ensures accuracy for records and follow-up.

Essential Verification Checklist:
1.  **Full Name Spelling:**
    - Example: 'Thank you, [Patient Name]. Could you please spell your last name for me to ensure I have it correct?'
2.  **Phone Number:**
    - Example: 'And could you verify the best phone number to reach you at?'
3.  **Date of Birth (If required by clinic protocol for identification):**
    - Example: 'To ensure I pull up the correct record, could you also please provide your date of birth?'

Optional (Based on call flow/clinic needs):
- Email Address
- Physical Address
""",

    "examples_empathy.txt": """
Best Practice: Actively listen and acknowledge the patient's situation, pain, or frustration to build rapport and show you care. Use validating and supportive language.

Example Empathetic Phrases:
- When patient describes pain/discomfort:
    - 'I'm really sorry to hear you're experiencing that pain in your [body part]. That sounds very uncomfortable.'
    - 'I understand that must be difficult to deal with.'
    - 'Thank you for explaining that. Let's see what we can do to help.'
- When patient expresses frustration (e.g., with previous treatment, waiting):
    - 'I can understand why you would feel frustrated in that situation.'
    - 'That sounds like a challenging experience.'
    - 'Let's work together to find a solution/get you the help you need.'
- General Acknowledgement:
    - 'Okay, I understand.' (Use sincerely, not dismissively)
    - 'Thank you for sharing that with me.'
""",

    "checklist_mva.txt": """
Best Practice: If the patient indicates the reason for their call might be related to a Motor Vehicle Accident (MVA) or Workers Compensation (W/C), systematically gather specific details required for these case types.

MVA/WC Initial Question:
- 'Is this condition or injury related to an accident, either a car accident (MVA) or an incident at work (Workers Comp)?'

If YES to MVA:
- Date of the accident?
- State where the accident occurred?
- What was your role (e.g., driver, passenger, pedestrian)?
- Were airbags deployed? Was a seatbelt worn?
- Were you taken by ambulance or other transport to a healthcare facility?
    - If yes, which facility?
- Do you have auto insurance claim information? (Insurer, Claim #, Adjuster Name/Contact #)
- Are you currently working with an attorney regarding the accident? (If yes, get Attorney Name/Contact #)

If YES to W/C:
- Date of the work injury?
- Employer at the time of injury?
- Do you have Workers Compensation claim information? (Insurer, Claim #, Adjuster Name/Contact #)
- Are you working with an attorney? (If yes, get Attorney Name/Contact #)
""",

    "info_out_of_network.txt": """
Best Practice: Clearly and proactively disclose if the practice is out-of-network (OON) with the patient's insurance *before* confirming an appointment. This manages expectations regarding potential costs. The ideal time is usually during or immediately after discussing their insurance information.

Example Disclosure Script:
'Thank you for providing your insurance information. I do want to let you know that [Clinic Name] is considered an out-of-network provider with most insurance plans, including [Mention Patient's Plan if known, e.g., Aetna].'

Explanation to include:
'Being out-of-network means that while you can absolutely receive care here, your insurance plan might cover a smaller portion of the costs compared to an in-network facility. This could result in a higher out-of-pocket responsibility for you, such as paying towards a deductible or a larger coinsurance.'

Offer Next Steps:
'We are happy to provide you with a superbill (a detailed receipt) after your visit, which you can submit to your insurance company for any potential direct reimbursement based on your plan's out-of-network benefits. Would you like to proceed with scheduling knowing we are out-of-network?'
"""
}

def create_knowledge_files():
    """Creates the knowledge base directory and populates it with files."""
    print(f"Attempting to create knowledge base in directory: '{KB_DIRECTORY}'")

    # Create the directory if it doesn't exist
    try:
        os.makedirs(KB_DIRECTORY, exist_ok=True)
        print(f"Directory '{KB_DIRECTORY}' ensured.")
    except OSError as e:
        print(f"Error creating directory {KB_DIRECTORY}: {e}")
        return # Stop if directory creation fails

    # Loop through the defined content and create files
    for filename, content in knowledge_content.items():
        filepath = os.path.join(KB_DIRECTORY, filename)
        print(f"Processing file: {filepath}")

        # Check if file already exists to avoid accidental overwrites
        # Remove this 'if' block if you WANT to overwrite existing files every time
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Write content, removing leading/trailing whitespace from the heredoc
                    f.write(content.strip())
                print(f"  Successfully created: {filename}")
            except IOError as e:
                print(f"  Error writing file {filename}: {e}")
        else:
            print(f"  Skipped (already exists): {filename}")

    print("\nKnowledge base file generation process complete.")

if __name__ == "__main__":
    create_knowledge_files()