# analysis_parser.py
import json
import re # Regular expressions for more robust JSON extraction

def parse_gemini_response(response_text: str) -> dict | None:
    """
    Parses the raw text response from Gemini, expecting a JSON object.
    Attempts to handle potential markdown code blocks or surrounding text.

    Args:
        response_text: The raw string response from the Gemini API.

    Returns:
        A dictionary representing the parsed JSON analysis,
        or None if parsing fails.
    """
    if not response_text:
        print("Error: No response text provided for parsing.")
        return None

    print("Attempting to parse Gemini JSON response...")

    # 1. Try direct JSON parsing first (ideal case)
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("Direct JSON parsing failed. Trying to extract JSON block...")
        pass # Continue to extraction methods

    # 2. Try extracting JSON within ```json ... ``` markdown blocks
    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)
    if match:
        json_string = match.group(1)
        print("Found JSON block within ```json ``` markers.")
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing extracted JSON block: {e}")
            print("--- Extracted String ---")
            print(json_string)
            print("--- End Extracted String ---")
            return None # Parsing failed

    # 3. Try extracting the first '{' to the last '}' as a fallback
    json_start = response_text.find('{')
    json_end = response_text.rfind('}')
    if json_start != -1 and json_end != -1 and json_end > json_start:
        json_string = response_text[json_start:json_end+1]
        print("Found JSON block using simple '{' and '}' search.")
        try:
            # Sometimes Gemini might add trailing commas which are invalid JSON
            # Basic attempt to remove trailing comma before closing brace/bracket
            cleaned_json_string = re.sub(r",\s*(\}|\])", r"\1", json_string)
            return json.loads(cleaned_json_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing fallback JSON block: {e}")
            print("--- Fallback String ---")
            print(json_string) # Print original string found
            print("--- End Fallback String ---")
            return None # Parsing failed

    # 4. If all methods fail
    print("Error: Could not find or parse a valid JSON object in the response.")
    print("--- Raw Response Text ---")
    print(response_text)
    print("--- End Raw Response Text ---")
    return None

# --- Example Usage (Optional) ---
# if __name__ == "__main__":
#     # Test cases
#     valid_json_text = '{"key": "value", "list": [1, 2]}'
#     markdown_json_text = "Some text before ```json\n{\"key\": \"value\", \"nested\": {\"a\": 1}}\n``` Some text after."
#     simple_markers_text = "Blah blah { \"key\": \"value\" , \"num\": 5 } blah"
#     invalid_text = "This is not JSON."
#     text_with_trailing_comma = '{"key": "value", "list": [1, 2,], }' # Invalid JSON

#     print("--- Testing Valid JSON ---")
#     parsed = parse_gemini_response(valid_json_text)
#     print(parsed)

#     print("\n--- Testing Markdown JSON ---")
#     parsed = parse_gemini_response(markdown_json_text)
#     print(parsed)

#     print("\n--- Testing Simple Markers JSON ---")
#     parsed = parse_gemini_response(simple_markers_text)
#     print(parsed)

#     print("\n--- Testing Invalid Text ---")
#     parsed = parse_gemini_response(invalid_text)
#     print(parsed)

#     print("\n--- Testing Trailing Comma JSON ---")
#     parsed = parse_gemini_response(text_with_trailing_comma)
#     print(parsed)