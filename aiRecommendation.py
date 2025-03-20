import requests
import os
import sys
import time

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "reports")
LOG_FILE_PATH = os.path.join(LOG_DIR, "scanner_file.txt")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "aiReport")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ai_report.txt")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"  # Replace if needed

# Rate limit settings
MAX_CHARS_PER_REQUEST = 6000  # Conservative estimate (1 token ≈ 4 characters)
CHUNK_OVERHEAD = 500          # Space for prompts and formatting
MAX_RETRIES = 3
RETRY_DELAY = 5
REQUEST_DELAY = 1.5

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def read_and_chunk_log(path):
    """Split log into manageable character-limited chunks"""
    try:
        with open(path, "r") as file:
            log_data = file.read()

        chunks = []
        current_chunk = []
        current_count = 0
        
        for line in log_data.split('\n'):
            line_length = len(line)
            if current_count + line_length > (MAX_CHARS_PER_REQUEST - CHUNK_OVERHEAD):
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_count = 0
            current_chunk.append(line)
            current_count += line_length

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    except Exception as e:
        print(f"Error processing log file: {e}")
        return []

def query_with_retry(prompt, chunk_num):
    """Handle API requests with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Analyze logs for security vulnerabilities. Provide concise steps."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.7
            }

            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait = RETRY_DELAY * (attempt + 1)
                print(f"Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"API Error: {str(e)}")
                return None
    return None

def save_output(content):
    """Save aggregated results to file"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_FILE, "w") as file:
            file.write(content)
        print(f"\nReport saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving output: {e}")

def main():
    chunks = read_and_chunk_log(LOG_FILE_PATH)
    if not chunks:
        print("No log data processed. Exiting.")
        return

    print(f"Processing {len(chunks)} log chunks...")
    full_report = []

    for i, chunk in enumerate(chunks, 1):
        print(f"\nAnalyzing chunk {i}/{len(chunks)}")
        prompt = f"Analyze these log entries for security issues:\n{chunk}\nFocus on critical vulnerabilities."

        result = query_with_retry(prompt, i)
        
        if result and "choices" in result:
            response = result["choices"][0]["message"]["content"]
            full_report.append(f"\n\n--- Chunk {i} Analysis ---\n{response}")
            time.sleep(REQUEST_DELAY)
        else:
            print(f"Failed to process chunk {i}")

    if full_report:
        final_report = "SECURITY ANALYSIS REPORT\n" + "\n".join(full_report)
        print("\nFinal Report Summary:")
        print(final_report[:500] + "...")  # Preview first 500 characters
        save_output(final_report)
    else:
        print("No analysis generated from any chunks")

if __name__ == "__main__":
    main()