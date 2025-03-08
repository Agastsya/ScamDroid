import subprocess
import sys
import os
import datetime
import webbrowser

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"  # Reset color

LOG_DIR = "/home/kali/Downloads/scanDroid/"
LOG_FILE = f"{LOG_DIR}scan_log.txt"
HTML_LOG_FILE = f"{LOG_DIR}scan_log.html"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def log_result(scan_type, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {scan_type} Results:\n{result}\n\n")
    
    with open(HTML_LOG_FILE, "a") as html_log:
        html_log.write(f"<h2>{scan_type} Results ({timestamp})</h2><pre>{result}</pre><hr>")

def run_nmap_scan(target_ip):
    print(f"{GREEN}Running Nmap scan on {target_ip}...{RESET}")
    result = subprocess.run(['nmap', '-sV', target_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Nmap scan results:\n{RESET}{output}")
    log_result("Nmap Scan", output)

def run_lynis_scan():
    print(f"{GREEN}Running Lynis audit...{RESET}")
    result = subprocess.run(['sudo', 'lynis', 'audit', 'system'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Lynis audit results:\n{RESET}{output}")
    log_result("Lynis Audit", output)

def run_port_scan(target_ip):
    print(f"{GREEN}Running Port Scan on {target_ip}...{RESET}")
    result = subprocess.run(['nmap', '-p-', target_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Port scan results:\n{RESET}{output}")
    log_result("Port Scan", output)

def check_vulnerabilities(target_ip):
    print(f"{GREEN}Checking vulnerabilities on {target_ip}...{RESET}")
    result = subprocess.run(['nmap', '--script', 'vuln', target_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Vulnerability scan results:\n{RESET}{output}")
    log_result("Vulnerability Scan", output)

def ai_patch_recommendations():
    print(f"{GREEN}Fetching AI-based patch recommendations...{RESET}")
    # Placeholder for AI-based recommendations logic
    recommendations = "Update OpenSSL, apply latest security patches, restrict SSH access."
    print(f"{CYAN}Recommended Patches:\n{RESET}{recommendations}")
    log_result("AI Patch Recommendations", recommendations)

def patch_vulnerabilities():
    print(f"{GREEN}Applying available patches...{RESET}")
    result = subprocess.run(['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Patch results:\n{RESET}{output}")
    log_result("Patch Updates", output)

def view_logs():
    print(f"{GREEN}Opening log file in web browser...{RESET}")
    webbrowser.open(HTML_LOG_FILE)

def clear_logs():
    print(f"{GREEN}Clearing log files...{RESET}")
    open(LOG_FILE, 'w').close()
    open(HTML_LOG_FILE, 'w').close()
    print(f"{CYAN}Log files cleared.{RESET}")

def main():
    if os.geteuid() != 0:
        print(f"{RED}This script requires root privileges. Please run with 'sudo'.{RESET}")
        sys.exit(1)
    
    while True:
        try:
            print(f"\n{YELLOW}Choose an option:{RESET}")
            print(f"{BLUE}1){RESET} {GREEN}Nmap Scan{RESET}")
            print(f"{BLUE}2){RESET} {GREEN}Lynis Scan{RESET}")
            print(f"{BLUE}3){RESET} {GREEN}Port Scan{RESET}")
            print(f"{BLUE}4){RESET} {GREEN}Vulnerability Scan (Nmap Script){RESET}")
            print(f"{BLUE}5){RESET} {GREEN}AI-Based Patch Recommendations{RESET}")
            print(f"{BLUE}6){RESET} {GREEN}Apply Patches Automatically{RESET}")
            print(f"{BLUE}7){RESET} {GREEN}View Logs{RESET}")
            print(f"{BLUE}8){RESET} {GREEN}Clear Logs{RESET}")
            print(f"{BLUE}9){RESET} {GREEN}Convert Logs to CSV{RESET}")
            print(f"{BLUE}10){RESET} {GREEN}Exit{RESET}")
            
            choice = int(input(f"\n{CYAN}Enter your choice (1-9): {RESET}"))
            
            if choice == 1:
                ip = input(f"{YELLOW}Enter target IP: {RESET}")
                run_nmap_scan(ip)
            elif choice == 2:
                run_lynis_scan()
            elif choice == 3:
                ip = input(f"{YELLOW}Enter target IP: {RESET}")
                run_port_scan(ip)
            elif choice == 4:
                ip = input(f"{YELLOW}Enter target IP: {RESET}")
                check_vulnerabilities(ip)
            elif choice == 5:
                ai_patch_recommendations()
            elif choice == 6:
                patch_vulnerabilities()
            elif choice == 7:
                view_logs()
            elif choice == 10:
                print(f"{GREEN}Exiting...{RESET}")
                break
            else:
                print(f"{RED}Invalid choice. Please select between 1-9.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a numeric value.{RESET}")

if __name__ == "__main__":
    main()
