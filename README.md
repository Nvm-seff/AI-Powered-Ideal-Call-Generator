# ✨ AI-Powered Ideal Call Generation ✨

**Analyze real patient calls, identify areas for improvement based on KPIs, and automatically generate ideal call scripts and audio for agent training using AI.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

This project provides an AI-driven solution to enhance customer support quality in healthcare settings. It processes recorded patient calls (or their raw transcripts) to:

1. **Structure the Dialogue:** Automatically format raw transcripts and assign speaker labels (Agent/Patient) using Google Gemini.
2. **Analyze Performance:** Evaluate the agent's performance against predefined Key Performance Indicators (KPIs), identify mistakes, and assess soft skills like empathy and tone using Google Gemini.
3. **Generate Ideal Responses:** Leverage a Retrieval-Augmented Generation (RAG) approach. Based on the analysis, it retrieves relevant best practices from a knowledge base and uses Google Gemini to generate an improved, "ideal" call script.
4. **Synthesize Audio:** Convert the generated ideal call script into realistic audio using the ElevenLabs Text-to-Speech API, creating ready-to-use training material.

The ultimate goal is to provide actionable feedback and concrete examples of best practices, helping agents improve communication clarity, accuracy, empathy, and overall service quality.

## 🛠️ Core Functions

- **🗣️ AI Diarization:** Converts raw, unstructured call transcripts into formatted dialogue with speaker labels (`AGENT:`, `PATIENT:`).
- **📊 KPI Analysis:** Checks agent adherence to a comprehensive list of configurable KPIs (e.g., introductions, verifications, information gathering, disclosures).
- **🚫 Mistake Identification:** Pinpoints specific errors or omissions made by the agent during the call.
- **💬 Soft Skill Assessment:** Evaluates qualitative aspects like confidence, tone, empathy, and conversation flow.
- **📚 RAG-Powered Generation:** Retrieves relevant best practices or script examples from a local knowledge base based on identified shortcomings before generating the ideal call.
- **💡 Ideal Call Scripting:** Generates text scripts demonstrating how the call _should_ have ideally been handled, incorporating best practices and addressing identified mistakes.
- **🔊 Realistic Audio Synthesis:** Creates high-quality audio versions of the ideal call scripts using customizable ElevenLabs voices.
- **🔧 Modular Design:** Code is structured into distinct modules for clarity and maintainability (configuration, KPIs, processing, API clients, RAG, TTS).

## ⚙️ How It Works (Workflow)

```mermaid
graph TD
    A[Raw Audio Call .mp3] --> B[External Whisper Transcription]
    B --> C[Raw Text Transcript]
    C --> D[Gemini Diarization]
    D --> E[Formatted Transcript with Speaker Labels]
    E --> F[Gemini Analysis]
    F --> G[Analysis Report JSON]
    G --> H[Identify Retrieval Queries]
    H --> I[RAG Retriever]
    J[Knowledge Base .txt files] --> I
    I --> K[Retrieved Knowledge]

    E --> L[Gemini RAG Generation]
    G --> L
    K --> L

    L --> M[Ideal Call Script Text]
    M --> N[ElevenLabs TTS]
    N --> O[Ideal Call Audio .mp3]

    style J fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#ccf,stroke:#333,stroke-width:2px
````

### Input:

- Starts with a raw audio call file (.mp3).

### Steps:

- **Transcription (External):** Use a Speech-to-Text engine (like locally hosted Whisper) to get a raw text transcript.
- **Diarization:** The raw text is sent to Google Gemini to add AGENT: and PATIENT: labels and structure the dialogue.
- **Analysis:** The formatted transcript and the list of KPIs (kpis.py) are sent to Google Gemini for evaluation. Gemini returns a structured JSON report detailing KPI adherence, mistakes, and soft skills assessment.
- **Retrieval (RAG):** Based on the mistakes and missed KPIs in the analysis report, the retriever.py module identifies relevant keywords and fetches corresponding best practice snippets or examples from the knowledge_base/ directory.
- **Generation (RAG):** The original formatted transcript, the analysis report, and the retrieved knowledge chunks are combined into a prompt for Google Gemini. Gemini generates an improved "ideal" call script text, guided by the retrieved best practices.
- **TTS Synthesis:** The generated ideal script text is processed line by line. Each utterance is sent to the ElevenLabs API using pre-configured voices for the Agent and Patient. The resulting audio chunks are streamed and saved as a single .mp3 file.

### Output:

- The process yields the analysis report (`_analysis.json`), the ideal call script (`_ideal_call_rag.txt`), and the ideal call audio (`_ideal_call_audio.mp3`).

## 🖥️ Technology Stack

- Python 3.x
- Google Gemini API (google-generativeai)
- ElevenLabs API (elevenlabs)
- OpenAI Whisper (assumed externally for Speech-to-Text)
- python-dotenv (for secure API key management)

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.8+ installed
- Access to Google Gemini API (API Key)
- Access to ElevenLabs API (API Key and Voice IDs)
- An external process or tool for audio-to-text transcription (e.g., Whisper). This project assumes you already have the raw text output.

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-call-analyzer.git
cd ai-call-analyzer
```

### 3. Set Up Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

(Note: If requirements.txt does not exist yet, run below to generate it:)

```bash
pip install google-generativeai python-dotenv elevenlabs
pip freeze > requirements.txt
```

### 5. Configure API Keys and Settings

- Create a `.env` file in the project root:

```
# .env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
ELEVENLABS_API_KEY=YOUR_ELEVENLABS_API_KEY
```

(IMPORTANT: Add `.env` to `.gitignore` to avoid committing secrets!)

- Edit `config.py`:

  - Ensure `AGENT_SPEAKER_LABEL` and `PATIENT_SPEAKER_LABEL` match expected diarization outputs.
  - Replace placeholder Voice IDs with valid ElevenLabs IDs:

```python
AGENT_VOICE_ID = "YOUR_AGENT_VOICE_ID"  # e.g., "21m00Tcm4TlvDq8ikWAM"
PATIENT_VOICE_ID = "YOUR_PATIENT_VOICE_ID"  # e.g., "AZnzlk1XvdvUeBnXmlld"
```

```
- Adjust `GEMINI_MODEL_NAME` or `ELEVENLABS_MODEL` if needed.
```

### 6. Populate Knowledge Base

```bash
python populate_knowledge_base.py
```

- Edit `.txt` files inside the `knowledge_base/` directory with your clinic's procedures, best practices, and example scripts.
- Update `KEYWORD_TO_FILE_MAP` in `retriever.py` if you change filenames or keyword triggers.

### 7. Prepare Input Transcript

- Place your raw, unstructured transcript file (e.g., from Whisper) in the project directory, e.g., `whisper_output.txt`.

### 8. Run the Main Script

- Update the `raw_transcript_file` variable in `main.py`:

```python
raw_transcript_file = "whisper_output.txt"  # Or your actual filename
```

- Run:

```bash
python main.py
```

### 9. Check Outputs

The script will generate:

- `*_diarized.txt`: Transcript formatted with speaker labels
- `*_analysis.json`: KPI analysis report
- `*_ideal_call_rag.txt`: Generated ideal call script
- `*_ideal_call_audio.mp3`: Synthesized ideal call audio

## 🔑 Configuration

- **API Keys:** Managed via `.env`
- **Voice IDs & Models:** Set in `config.py`
- **Speaker Labels:** Defined in `config.py`
- **KPIs:** Listed in `kpis.py` (customize as needed)
- **RAG Knowledge:** Stored as `.txt` files in `knowledge_base/`; mapping in `retriever.py`

## 📁 Project Structure

```
ai_call_analyzer/
├── knowledge_base/         # RAG knowledge files (.txt)
├── .env                    # API keys (!!! Add to .gitignore !!!)
├── config.py               # Configurations
├── kpis.py                 # KPI definitions
├── main.py                 # Main orchestration script
├── prompt_builder.py       # Prompt construction functions
├── transcript_processor.py # Transcript loading functions
├── gemini_client.py        # Google Gemini API client
├── analysis_parser.py      # Parses analysis responses
├── retriever.py            # RAG retrieval logic
├── tts_generator.py        # ElevenLabs TTS client
├── populate_knowledge_base.py # Helper script
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## 🔮 Future Enhancements

- Vector Database RAG (e.g., ChromaDB, FAISS) for better semantic retrieval
- Web Interface (Streamlit or Flask) for easier interaction
- Advanced Audio Analysis (e.g., silences, interruptions, sentiment)
- Batch Processing support
- Database Integration for result storage and reporting
- Improved Error Handling and Reporting
