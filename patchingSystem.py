import json
import subprocess
import re
import sys
from datetime import datetime

def extract_json_blobs(text):
    """Extract all JSON blocks from the text."""
    return re.findall(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)

def clean_json_block(block):
    """Remove line comments (starting with //) from a JSON block."""
    cleaned_lines = []
    for line in block.splitlines():
        if line.strip().startswith("//"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def extract_commands_from_data(data, commands):
    """Recursively extract commands and their descriptions from the data structure."""
    if isinstance(data, dict):
        # Check for command(s) keys at this level
        for key in ["command", "commands"]:
            if key in data:
                cmd = data[key]
                desc = data.get("description") or data.get("action") or ""
                if isinstance(cmd, str):
                    commands.append((cmd, desc))
                elif isinstance(cmd, list):
                    for item in cmd:
                        commands.append((item, desc))
        # Recursively search all dictionary values
        for value in data.values():
            extract_commands_from_data(value, commands)
    elif isinstance(data, list):
        for item in data:
            extract_commands_from_data(item, commands)

def extract_commands(json_blocks):
    """Extract all commands and descriptions from the parsed JSON blobs."""
    commands = []
    for block in json_blocks:
        cleaned_block = clean_json_block(block)
        try:
            data = json.loads(cleaned_block)
            extract_commands_from_data(data, commands)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return commands

def is_editor_command(command):
    """Return True if the command invokes an interactive text editor."""
    # Check for common editors such as nano, vi, vim, or emacs.
    return bool(re.search(r'\b(nano|vi|vim|emacs)\b', command))

def run_command(command, description, log_file):
    # Skip commands that are interactive editor commands
    if is_editor_command(command):
        print(f"⏩ Skipping interactive editor command: {command}")
        return

    print(f"🔧 Running: {command}")
    print(f"📌 Purpose: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        status = "✅ SUCCESS"
        output = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        status = "❌ FAILED"
        output = e.stderr.strip()

    log_entry = (
        f"[{datetime.now()}]\n"
        f"COMMAND: {command}\n"
        f"DESCRIPTION: {description}\n"
        f"STATUS: {status}\n"
        f"OUTPUT:\n{output}\n{'-'*60}\n"
    )
    with open(log_file, "a") as f:
        f.write(log_entry)

    print(f"{status}\n{'-'*60}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python security_fixer.py <path_to_log_file>")
        sys.exit(1)

    log_path = sys.argv[1]
    log_output = "security_fix_results.log"

    try:
        with open(log_path, "r") as file:
            content = file.read()

        print("📄 Parsing JSON blocks from log file...")
        json_blobs = extract_json_blobs(content)
        commands = extract_commands(json_blobs)

        print(f"🔍 Found {len(commands)} fix commands (editor commands will be skipped).")
        print("🚀 Starting execution...\n")

        for cmd, desc in commands:
            run_command(cmd, desc, log_output)

        print(f"✅ All commands processed. Log written to: {log_output}")

    except FileNotFoundError:
        print(f"❌ Log file not found: {log_path}")

if __name__ == "__main__":
    main()
