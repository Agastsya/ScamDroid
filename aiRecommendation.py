import requests
import os
import sys

# Define file paths and Groq API endpoint
LOG_FILE_PATH = "/home/kali/Downloads/finalScanner/app.txt"
OUTPUT_DIR = "/home/kali/Downloads/finalScanner/aiReport/"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ai_report.txt")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Use the provided Groq API key
API_KEY = {API_KEY} 
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def read_log_file(path):
    """Reads the log file and returns its contents as a string."""
    try:
        with open(path, "r") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return ""

def query(prompt):
    """Sends a request to the Groq API with the given prompt."""
    payload = {
        "model": "llama-3.3-70b-versatile",  # Free-tier model
        "messages": [
            {"role": "system", "content": "You are a cybersecurity expert. Analyze the provided python website code data and find vulnerabilities inside it in detail."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,  # Adjust as needed
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def save_output(content):
    """Saves the generated recommendations to a file and captures terminal output."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the directory exists

        # Redirect stdout and stderr to the file
        with open(OUTPUT_FILE, "w") as file:
            sys.stdout = file  # Redirect standard output to file
            sys.stderr = file  # Redirect errors to file

            print(" Output saved to:", OUTPUT_FILE)
            print("Generated Recommendations:\n", content)

        # Restore stdout and stderr to the console
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        print(f" Output also saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f" Error saving output: {e}")

def main():
    # Read the log file content
    log_data = read_log_file(LOG_FILE_PATH)
    if not log_data:
        print("No log data found. Exiting.")
        return

    # Build the prompt
    prompt = f"Here is the log data:\n{log_data}\n\nPlease analyze it and provide cybersecurity recommendations."

    # Query the Groq API
    result = query(prompt)
    
    if result and "choices" in result:
        output_text = result["choices"][0]["message"]["content"]
        print("Generated Recommendations:\n", output_text)
        save_output(output_text)  # Save both API response and terminal output
    else:
        print("Failed to generate recommendations.")

if __name__ == "__main__":
    main()
