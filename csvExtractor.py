# csvExtractor.py (final working version)
import csv
import re
import os
import sys
import argparse
from datetime import datetime

CSV_COLUMNS = [
    "Datetime (when it was scanned)",
    "Vulnerability",
    "MachineImpacted",
    "Severity",
    "Vulnerability Description",
    "Vuln_ID (FK)",
    "Mach_id (FK)",
    "Machine_name",
    "Machine_OS",
    "Fix",
    "Patch status",
    "Log"
]

def extract_vulnerabilities(log_content):
    """Robust vulnerability extraction from Lynis logs"""
    vulnerabilities = []
    
    # Extract machine info
    machine_role = re.search(r'Machine\s*role:\s*(\w+)', log_content, re.IGNORECASE)
    machine_role = machine_role.group(1).strip() if machine_role else "server"
    
    machine_os = re.search(r'Operating\s*system:\s*(.+)', log_content, re.IGNORECASE)
    machine_os = machine_os.group(1).strip() if machine_os else "Linux"
    
    hostname = re.search(r'Hostname:\s*(\S+)', log_content, re.IGNORECASE)
    machine_name = hostname.group(1).strip() if hostname else "unknown"

    # Process log lines
    current_vuln = None
    for line in log_content.split('\n'):
        line = line.strip()
        
        # Detect test sections
        test_match = re.search(r'Test:\s*(.+)', line)
        if test_match:
            current_vuln = {
                "Vulnerability": test_match.group(1),
                "Vuln_ID (FK)": "N/A",
                "Severity": "Medium",
                "Vulnerability Description": "",
                "Fix": "",
                "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "MachineImpacted": machine_role,
                "Mach_id (FK)": "MACH_001",
                "Machine_name": machine_name,
                "Machine_OS": machine_os,
                "Patch status": "Pending",
                "Log": line
            }
            continue
        
        # Detect results
        if current_vuln:
            if 'Result:' in line:
                current_vuln["Vulnerability Description"] += line.split("Result:")[1].strip() + ". "
                if any(kw in line.lower() for kw in ['missing', 'vulnerable', 'unsecured']):
                    current_vuln["Severity"] = "High"
            elif 'Suggestion:' in line:
                current_vuln["Fix"] = line.split("Suggestion:")[1].strip()
            elif '====' in line:  # End of section
                vulnerabilities.append(current_vuln)
                current_vuln = None

    return vulnerabilities

def write_csv(output_path, data):
    """Guaranteed CSV creation"""
    try:
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for item in data:
                writer.writerow({k: v[:500] if isinstance(v, str) else v for k, v in item.items()})
        return True
    except Exception as e:
        print(f"CSV Error: {str(e)}")
        return False

def main(args=None):
    parser = argparse.ArgumentParser(description="Lynis Log to CSV Converter")
    parser.add_argument("--source", required=True, help="Input log file/directory")
    parser.add_argument("--output_dir", required=True, help="Output directory for CSV")
    
    args = parser.parse_args(args if args else sys.argv[1:])

    # Validate paths
    if not os.path.exists(args.source):
        print(f"Error: Source path '{args.source}' doesn't exist")
        return

    try:
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Process files
        files = []
        if os.path.isdir(args.source):
            files = [os.path.join(args.source, f) for f in os.listdir(args.source) 
                    if f.endswith(('.txt', '.log'))]
        else:
            files = [args.source]

        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                vulns = extract_vulnerabilities(content)
                if vulns:
                    output_file = os.path.join(
                        args.output_dir,
                        f"{os.path.basename(file_path).rsplit('.', 1)[0]}_report.csv"
                    )
                    if write_csv(output_file, vulns):
                        print(f"Created: {output_file}")
                    else:
                        print(f"Failed: {output_file}")
                else:
                    print(f"No vulnerabilities in {os.path.basename(file_path)}")

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    except Exception as e:
        print(f"Critical Error: {str(e)}")

if __name__ == "__main__":
    main()