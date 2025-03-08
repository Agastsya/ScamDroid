import csv
import re
import argparse
import os
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
    "Last_active",
    "last_logged_inuser",
    "ip_address",
    "Fix",
    "Date/time",
    "True/False",
    "Patch status",
    "Log"
]

def extract_vulnerabilities(log_content):
    """Extract vulnerabilities from Lynis log content."""
    vulnerabilities = []
    
    # Extract machine role (default: server)
    machine_role = re.search(r'machine-role=(\w+)', log_content)
    machine_role = machine_role.group(1).strip() if machine_role else "server"
    
    # Extract machine OS and hostname
    os_match = re.search(r'Operating system:\s*(.+)$', log_content, re.MULTILINE)
    machine_os = os_match.group(1).strip() if os_match else "Linux"
    
    hostname_match = re.search(r'Hostname:\s*(\S+)', log_content, re.MULTILINE)
    machine_name = hostname_match.group(1).strip() if hostname_match else machine_role

    # Track current test ID and related data during line processing
    current_test_id = None
    current_vuln = {}
    lines = log_content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for test ID section start
        test_id_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Performing test ID (\w+-\d+)', line)
        if test_id_match:
            if current_vuln:
                vulnerabilities.append(current_vuln)
                current_vuln = {}
            current_test_id = test_id_match.group(1)
            current_vuln = {
                "Vuln_ID (FK)": current_test_id,
                "Vulnerability Description": "",
                "Fix": "",
                "Severity": "Medium"  # Default severity
            }
            continue

        # Check for end of test section (====)
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ====', line):
            if current_vuln:
                if current_vuln.get("Vulnerability Description"):
                    current_vuln.update({
                        "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "MachineImpacted": machine_role,
                        "Mach_id (FK)": "MACH_001",
                        "Machine_name": machine_name,
                        "Machine_OS": machine_os,
                        "Patch status": "Pending",
                    })
                    vulnerabilities.append(current_vuln)
                current_vuln = {}
            current_test_id = None
            continue

        # Process lines within a test section
        if current_test_id:
            # Capture Result lines
            result_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Result: (.*)', line)
            if result_match:
                result_text = result_match.group(1)
                current_vuln["Vulnerability Description"] += f"Result: {result_text}. "
                # Determine severity based on keywords
                if 'not found' in result_text.lower() or 'missing' in result_text.lower():
                    current_vuln["Severity"] = "High"
                # Check for critical issues
                if 'password' in result_text.lower() and 'expire' in result_text.lower():
                    current_vuln["Severity"] = "High"
                continue

            # Capture Suggestion lines
            suggestion_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Suggestion: (.*)', line)
            if suggestion_match:
                current_vuln["Fix"] = suggestion_match.group(1)
                continue

            # Capture specific account without expire date
            account_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Account without expire date: (\S+)', line)
            if account_match:
                account = account_match.group(1)
                vulnerabilities.append({
                    "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Vulnerability": "Account without expiration",
                    "MachineImpacted": machine_role,
                    "Severity": "High",
                    "Vulnerability Description": f"Account '{account}' has no password expiration date set (Test ID: AUTH-9282)",
                    "Vuln_ID (FK)": "AUTH-9282",
                    "Mach_id (FK)": "MACH_001",
                    "Machine_name": machine_name,
                    "Machine_OS": machine_os,
                    "Fix": "Set expire date for the account using 'chage' command",
                    "Patch status": "Pending",
                    "Log": "Found account without expire date"
                })
                continue

        # Directory check vulnerabilities (outside test IDs)
        dir_test_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Test: Checking (/.+)', line)
        if dir_test_match:
            dir_path = dir_test_match.group(1)
            # Look for corresponding Result line
            dir_result = next((l for l in lines if f"Result: directory {dir_path}" in l), None)
            if dir_result and ('could not be found' in dir_result or 'does not exist' in dir_result):
                vulnerabilities.append({
                    "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Vulnerability": dir_path,
                    "MachineImpacted": machine_role,
                    "Severity": "Medium",
                    "Vulnerability Description": f"Directory {dir_path} not found or inaccessible",
                    "Vuln_ID (FK)": f"DIR-{len(vulnerabilities)+1}",
                    "Mach_id (FK)": "MACH_001",
                    "Machine_name": machine_name,
                    "Machine_OS": machine_os,
                    "Fix": f"Create directory {dir_path} or check configuration",
                    "Patch status": "Pending",
                    "Log": dir_result.split("Result: ")[1]
                })

        # Kernel parameter checks (sysctl)
        kernel_missing_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Result: sysctl key (\S+) does not exist', line)
        if kernel_missing_match:
            param = kernel_missing_match.group(1)
            vulnerabilities.append({
                "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Vulnerability": param,
                "MachineImpacted": machine_role,
                "Severity": "High",
                "Vulnerability Description": f"Kernel parameter {param} is missing",
                "Vuln_ID (FK)": f"KRNL-{len(vulnerabilities)+1}",
                "Mach_id (FK)": "MACH_001",
                "Machine_name": machine_name,
                "Machine_OS": machine_os,
                "Fix": f"Add kernel parameter {param} with recommended value",
                "Patch status": "Pending",
                "Log": "Parameter not found in sysctl"
            })

        # UMASK configuration issues
        umask_match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Result: umask value is not configured', line)
        if umask_match:
            vulnerabilities.append({
                "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Vulnerability": "UMASK Configuration",
                "MachineImpacted": machine_role,
                "Severity": "Medium",
                "Vulnerability Description": "Default umask is not properly configured (Test ID: AUTH-9328)",
                "Vuln_ID (FK)": "AUTH-9328",
                "Mach_id (FK)": "MACH_001",
                "Machine_name": machine_name,
                "Machine_OS": machine_os,
                "Fix": "Configure umask in /etc/login.defs to 027 or stricter",
                "Patch status": "Pending",
                "Log": "Umask configuration missing"
            })

    # Add remaining vulnerability if any
    if current_vuln.get("Vulnerability Description"):
        current_vuln.update({
            "Datetime (when it was scanned)": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "MachineImpacted": machine_role,
            "Mach_id (FK)": "MACH_001",
            "Machine_name": machine_name,
            "Machine_OS": machine_os,
            "Patch status": "Pending",
        })
        vulnerabilities.append(current_vuln)

    return vulnerabilities

def write_csv(output_path, data):
    """Write extracted data to a CSV file."""
    try:
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error writing CSV to {output_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Extract vulnerabilities from Lynis logs and generate CSV reports.")
    parser.add_argument("--source", required=True, help="Path to log file/directory.")
    parser.add_argument("--output_dir", required=True, help="Directory to save CSV files.")
    args = parser.parse_args()

    try:
        os.makedirs(args.output_dir, exist_ok=True)
    except Exception as e:
        print(f"Failed to create output directory {args.output_dir}: {e}")
        return

    if os.path.isdir(args.source):
        log_files = [os.path.join(args.source, f) for f in os.listdir(args.source) if f.endswith('.txt')]
    else:
        log_files = [args.source]

    for log_file in log_files:
        print(f"Processing file: {log_file}")
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
            continue
        
        vulnerabilities = extract_vulnerabilities(log_content)
        print(f"Found {len(vulnerabilities)} vulnerabilities in {log_file}")
        
        if not vulnerabilities:
            print(f"No vulnerabilities found in {log_file}. Skipping report.")
            continue
        
        base_name = os.path.basename(log_file).replace('.txt', '')
        output_csv = os.path.join(args.output_dir, f"{base_name}_report.csv")
        if write_csv(output_csv, vulnerabilities):
            print(f"Successfully generated report: {output_csv}")
        else:
            print(f"Failed to generate report for {log_file}")

if __name__ == "__main__":
    main()
