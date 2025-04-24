# kpis.py
# List of Key Performance Indicators for call analysis

KPI_LIST = [
    # --- Introduction & Verification ---
    "Did the customer support representative introduce themselves to the patient?",
    "Did the customer support representative verify the name of the patient?",
    "Did the customer support representative verify the correct spelling of the patient's name?",
    "Did the customer support representative verify the phone number of the patient?",
    "Did the customer support representative capture the lead source?",

    # --- Medical Condition Inquiry ---
    "Did the customer support representative ask about the detailed description of the medical condition, including the affected body part?",
    "Did the customer support representative ask about the symptoms of the medical condition?",
    "Did the customer support representative ask about the duration or recurrence pattern of the medical condition?",

    # --- Case Type Identification ---
    "Did the customer support representative identify if the case was related to an MVA (Motor Vehicle Accident), W/C (Workers Compensation), or a legal case?",

    # --- Previous Treatment Inquiry ---
    "Did the customer support representative ask about or confirm any previous treatments?",
    "Did the customer support representative ask about or confirm the names of providers associated with previous treatments (if applicable)?",
    "Did the customer support representative ask about or confirm the contact numbers of providers associated with previous treatments (if applicable)?",
    "Did the customer support representative ask about or confirm which treatments or procedures were completed by previous providers?",
    "Did the customer support representative confirm prior diagnostic testing?",
    "Did the customer support representative ask the patient to bring records with them for the initial appointment?",

    # --- Accident Details (If MVA/WC) ---
    "Did the customer support representative ask about or confirm the date of the accident?",
    "Did the customer support representative ask about or confirm in which state the accident occurred?",
    "Did the customer support representative ask about a description of the accident?",
    "Did the customer support representative ask about or confirm the individual's role in the accident (e.g., driver, passenger, pedestrian)?",
    "Did the customer support representative ask about or confirm whether the airbags were deployed and if the seatbelt was worn?",
    "Did the customer support representative ask about or confirm if the individual was taken by ambulance or other transport to a healthcare facility?",
    "Did the customer support representative ask about or confirm which healthcare facility the individual was taken to?",

    # --- Claim/Attorney Information (If MVA/WC/Legal) ---
    "Did the customer support representative ask about or confirm the claim information correctly?",
    "Did the customer support representative ask about or confirm the adjuster information correctly?",
    "Did the customer support representative ask about or confirm the attorney, and if none was on file, offer to help coordinate a consultation so the patient can ask their own questions regarding their accident?",

    # --- Soft Skills & Communication ---
    "Did the customer support representative speak confidently to the patient?",
    "Did the customer support representative maintain a positive tone throughout the call?",
    "Did the customer support representative display consistent energy during the conversation?",
    "Did the customer support representative show enthusiasm while interacting with the patient?",
    "Was the customer support representative empathetic and relatable to the patient’s concerns?",
    "Did the customer support representative demonstrate the ability to steer the conversation?",
    "Did the customer support representative demonstrate the ability to engage in a genuine conversation with the patient, rather than just asking questions?",
    "Did the customer support representative maintain the conversation flow with little to no dead space?",

    # --- Upselling & Company Info ---
    "Did the customer support representative upsell equipment and/or services to the patient?",
    "Did the customer support representative upsell the company philosophy to the patient?",
    "Did the customer support representative share reviews or success stories (cash pay intakes) with the patient?",

    # --- Appointment Confirmation ---
    "Did the customer support representative confirm the appointment date with the patient?",
    "Did the customer support representative confirm the appointment time with the patient?",
    "Did the customer support representative confirm the provider or service with the patient?",
    "Did the customer support representative confirm the location or address with the patient?",
    "Did the customer support representative reiterate the next steps with the new patient packet and the BREEZE New Patient Portal (phone or tablet)?",

    # --- Insurance Information ---
    "Did the customer support representative ask for or confirm the insurance ID?",
    "Did the customer support representative ask for or confirm the insurance group?",
    "Did the customer support representative ask for or confirm the insurance subscriber?",
    "Did the customer support representative ask for the subscriber’s name (if not the patient)?",
    "Did the customer support representative ask for the subscriber’s date of birth (if not the patient)?",
    "Did the customer support representative ask about or confirm if there is a secondary insurer?",

    # --- Disclosures ---
    "Did the customer support representative disclose that we are an out-of-network practice?",
]

# You could add more structured info here if needed, e.g., categories
# KPI_CATEGORIES = { "Introduction": [...], "Medical": [...], ... }