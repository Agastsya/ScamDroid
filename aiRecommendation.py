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

# Updated timeout configuration
MAX_CHARS_PER_REQUEST = 5000 
CHUNK_OVERHEAD = 400          
MAX_RETRIES = 4               
RETRY_DELAY = 7               
REQUEST_DELAY = 5             
API_TIMEOUT = 45              

API_KEY = "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"  
if not API_KEY:
    print("Error: API key not found. Please set the GROQ_API_KEY environment variable.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def read_and_chunk_log(path):
    """Split log into manageable chunks with better error handling"""
    try:
        with open(path, "r") as file:
            log_data = file.read()

        chunks = []
        current_chunk = []
        current_count = 0
        
        # Smarter chunking with paragraph awareness
        for paragraph in log_data.split('\n\n'):
            para_length = len(paragraph)
            if current_count + para_length > (MAX_CHARS_PER_REQUEST - CHUNK_OVERHEAD):
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_count = 0
            current_chunk.append(paragraph)
            current_count += para_length

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    except Exception as e:
        print(f"Error processing log file: {e}")
        return []

def query_with_retry(prompt, chunk_num):
    """Improved retry logic with timeout handling"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Act like a Cybersecurity Professional/Engineer and then Analyze logs for security vulnerabilities and Provide concise steps in json format and provide specific commands for fixing vulnerabilities"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.7
            }

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"⌛ Timeout on chunk {chunk_num}, attempt {attempt}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES:
                backoff = RETRY_DELAY * attempt
                print(f"⏳ Retrying in {backoff} seconds...")
                time.sleep(backoff)
            continue
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Error: {str(e)}")
            return None

    print(f"❌ Failed to process chunk {chunk_num} after {MAX_RETRIES} attempts")
    return None

# Rest of the functions remain the same (save_output, main)

def save_output(content):
    """Save aggregated results to file"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_FILE, "w") as file:
            file.write(content)
        print(f"\n✅ Report saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error saving output: {e}")

def main():
    chunks = read_and_chunk_log(LOG_FILE_PATH)
    if not chunks:
        print("❌ No log data processed. Exiting.")
        return

    print(f"📊 Processing {len(chunks)} log chunks...")
    full_report = []

    for i, chunk in enumerate(chunks, 1):
        print(f"\n🔍 Analyzing chunk {i}/{len(chunks)}")
        prompt = f"Act like a Cybersecurity Professional/Engineer and then Analyze logs for security vulnerabilities and Provide concise steps in json format and provide specific commands for fixing vulnerabilities"

        result = query_with_retry(prompt, i)
        
        if result and "choices" in result:
            response = result["choices"][0]["message"]["content"]
            full_report.append(f"\n\n--- Chunk {i} Analysis ---\n{response}")
            time.sleep(REQUEST_DELAY)
        else:
            print(f"⚠️ Failed to process chunk {i}")

    if full_report:
        final_report = "🛡️ SECURITY ANALYSIS REPORT\n" + "\n".join(full_report)
        print("\n📄 Final Report Summary:")
        print(final_report[:500] + "...")
        save_output(final_report)
    else:
        print("⚠️ No analysis generated from any chunks")

if __name__ == "__main__":
    main()