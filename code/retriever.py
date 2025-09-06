# retriever.py
import os
from typing import List, Dict, Any

# --- Simple Knowledge Base Implementation ---
# In a real RAG system, this would query a vector database.
# For now, we use simple keyword matching on filenames/content.

KB_DIRECTORY = "knowledge_base"

# Map keywords (likely derived from analysis findings) to filenames
# This is a basic mapping, needs refinement based on actual analysis outputs
KEYWORD_TO_FILE_MAP = {
    "introduction": "sop_introduction.txt",
    "introduce": "sop_introduction.txt",
    "verify": "sop_verification.txt",
    "verification": "sop_verification.txt",
    "spelling": "sop_verification.txt",
    "phone number": "sop_verification.txt",
    "empathy": "examples_empathy.txt",
    "empathetic": "examples_empathy.txt",
    "relatable": "examples_empathy.txt",
    "mva": "checklist_mva.txt",
    "accident": "checklist_mva.txt",
    "out-of-network": "info_out_of_network.txt",
    "disclosure": "info_out_of_network.txt",
    # Add more mappings based on your KPIs and common mistakes
}

def load_knowledge_chunk(filename: str) -> str | None:
    """Loads content from a specific file in the knowledge base."""
    filepath = os.path.join(KB_DIRECTORY, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading knowledge file {filepath}: {e}")
            return None
    else:
        print(f"Warning: Knowledge file not found: {filepath}")
        return None

def retrieve_relevant_knowledge(analysis_report: Dict[str, Any], max_chunks: int = 3) -> List[str]:
    """
    Retrieves relevant knowledge chunks based on analysis findings.
    (Simple keyword-based retrieval for this example).

    Args:
        analysis_report: The parsed analysis JSON.
        max_chunks: Maximum number of distinct knowledge chunks to retrieve.

    Returns:
        A list of strings, where each string is the content of a relevant knowledge chunk.
    """
    retrieved_content = []
    retrieved_filenames = set() # Avoid retrieving the same file multiple times

    # Extract potential keywords from mistakes and missed KPIs
    potential_keywords = set()
    mistakes = analysis_report.get("overall_assessment", {}).get("mistakes_and_improvement_areas", [])
    missed_kpis = [item['kpi'] for item in analysis_report.get('kpi_analysis', []) if item.get('status') == 'Not Met']

    search_texts = mistakes + missed_kpis

    print("\nIdentifying keywords for knowledge retrieval...")
    for text in search_texts:
        text_lower = text.lower()
        for keyword, filename in KEYWORD_TO_FILE_MAP.items():
            if keyword in text_lower and filename not in retrieved_filenames:
                print(f"  - Found keyword '{keyword}', mapping to '{filename}'")
                content = load_knowledge_chunk(filename)
                if content:
                    retrieved_content.append(f"--- Relevant Knowledge: {filename} ---\n{content}\n--- End Knowledge ---")
                    retrieved_filenames.add(filename)
                    if len(retrieved_content) >= max_chunks:
                        break # Stop if we reached the limit
        if len(retrieved_content) >= max_chunks:
            break

    if not retrieved_content:
        print("No specific knowledge chunks retrieved based on keywords.")
    else:
        print(f"Retrieved {len(retrieved_content)} knowledge chunk(s).")

    return retrieved_content