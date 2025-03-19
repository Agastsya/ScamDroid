import subprocess
import sys
import os
import datetime
import webbrowser
from urllib.parse import urlparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"  

LOG_DIR = "/home/kali/Downloads/finalScanner/reports"
LOG_FILE = f"{LOG_DIR}/scanner_file.txt"
HTML_LOG_FILE = f"{LOG_DIR}/scanner_file.html"

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
    result = subprocess.run(['nmap', '-sV', target_ip],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Nmap scan results for {target_ip}:\n{RESET}{output}")
    log_result("Nmap Scan", f"Target: {target_ip}\n{output}")

def run_bandit_scan():
    print(f"{GREEN}Running Bandit code analysis...{RESET}")
    target_dir = input(f"{YELLOW}Enter directory path to scan (e.g., /home/projects): {RESET}")
    
    if not os.path.isdir(target_dir):
        print(f"{RED}ERROR: Invalid directory path{RESET}")
        return

    try:
        result = subprocess.run(
            ['bandit', '-r', target_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        print(f"{CYAN}Bandit scan results for {target_dir}:\n{RESET}{output}")
        log_result("Bandit Code Scan", f"Target: {target_dir}\n{output}")
    except FileNotFoundError:
        print(f"{RED}ERROR: Bandit command not found. Please install bandit with 'pip install bandit'{RESET}")
    except Exception as e:
        print(f"{RED}Error running Bandit scan: {e}{RESET}")

def run_lynis_scan():
    print(f"{GREEN}Running Lynis audit on the local system...{RESET}")
    result = subprocess.run(['sudo', 'lynis', 'audit', 'system'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Lynis audit results:\n{RESET}{output}")
    log_result("Lynis Audit", output)

def run_naabu_scanner(target_ip):
    print(f"{GREEN}Running Naabu scan on {target_ip}...{RESET}")
    try:
        result = subprocess.run(['naabu', '-host', target_ip],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
    except FileNotFoundError:
        print(f"{RED}ERROR: Naabu command not found. Please install Naabu.{RESET}")
        return
    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Naabu scan results for {target_ip}:\n{RESET}{output}")
    log_result("Naabu Scan", f"Target: {target_ip}\n{output}")

def run_gobuster_scan(target_url):
    # Validate URL
    parsed = urlparse(target_url)
    if not (parsed.scheme and parsed.netloc):
        print(f"{RED}ERROR: Your target is not a valid URL{RESET}")
        return

    print(f"{GREEN}Running Gobuster scan on {target_url}...{RESET}")
    try:
        result = subprocess.run([
            'gobuster', 'dir',
            '-u', target_url,
            '-w', '/usr/share/wordlists/dirb/common.txt',
            '-t', '50',
            '-fs', '318',
            '-b', ''
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print(f"{RED}ERROR: Gobuster command not found. Please install Gobuster.{RESET}")
        return

    output = result.stdout if result.returncode == 0 else result.stderr
    print(f"{CYAN}Gobuster scan results for {target_url}:\n{RESET}{output}")
    log_result("Gobuster Scan", f"Target: {target_url}\n{output}")

def run_ai_recommendations():
    print(f"{GREEN}Generating AI security recommendations...{RESET}")
    try:
        result = subprocess.run(
            ['python3', '/home/kali/Downloads/finalScanner/aiRecommendation.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        print(f"{CYAN}AI Recommendations:\n{RESET}{output}")
    except Exception as e:
        print(f"{RED}Error running AI recommendations: {e}{RESET}")

def view_logs():
    print(f"{GREEN}Opening log file in web browser...{RESET}")
    webbrowser.open(HTML_LOG_FILE)

def infra_scanner():
    while True:
        print(f"\n{YELLOW}Infra Scanner Options:{RESET}")
        print(f"{BLUE}1){RESET} {GREEN}Scan multiple IPs using Nmap{RESET}")
        print(f"{BLUE}2){RESET} {GREEN}Run Lynis scan{RESET}")
        print(f"{BLUE}3){RESET} {GREEN}Scan multiple IPs using Naabu{RESET}")
        print(f"{BLUE}4){RESET} {GREEN}Back to Main Menu{RESET}")
        
        try:
            choice = int(input(f"\n{CYAN}Enter your choice (1-4): {RESET}"))
            if choice == 1:
                ips = input(f"{YELLOW}Enter target IPs (comma-separated) for Nmap scan: {RESET}")
                ip_list = [ip.strip() for ip in ips.split(",") if ip.strip()]
                for ip in ip_list:
                    run_nmap_scan(ip)
            elif choice == 2:
                run_lynis_scan()
            elif choice == 3:
                ips = input(f"{YELLOW}Enter target IPs (comma-separated) for Naabu scan: {RESET}")
                ip_list = [ip.strip() for ip in ips.split(",") if ip.strip()]
                for ip in ip_list:
                    run_naabu_scanner(ip)
            elif choice == 4:
                break
            else:
                print(f"{RED}Invalid choice. Please select between 1-4.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a numeric value.{RESET}")

def web_scanner():
    while True:
        print(f"\n{YELLOW}Web Scanner Options:{RESET}")
        print(f"{BLUE}1){RESET} {GREEN}Run Gobuster scan (Replacing DirBuster){RESET}")
        print(f"{BLUE}2){RESET} {GREEN}Back to Main Menu{RESET}")
        
        try:
            choice = int(input(f"\n{CYAN}Enter your choice (1-2): {RESET}"))
            if choice == 1:
                url = input(f"{YELLOW}Enter target URL: {RESET}")
                run_gobuster_scan(url)
            elif choice == 2:
                break
            else:
                print(f"{RED}Invalid choice. Please select between 1-2.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a numeric value.{RESET}")

def main():
    if os.geteuid() != 0:
        print(f"{RED}This script requires root privileges. Please run with 'sudo'.{RESET}")
        sys.exit(1)
    
    while True:
        print(f"\n{YELLOW}Main Menu:{RESET}")
        print(f"{BLUE}1){RESET} {GREEN}Infra Scanner (Nmap, Lynis & Naabu){RESET}")
        print(f"{BLUE}2){RESET} {GREEN}Web Scanner (Gobuster){RESET}")
        print(f"{BLUE}3){RESET} {GREEN}Bandit Scanner{RESET}")
        print(f"{BLUE}4){RESET} {GREEN}View Logs{RESET}")
        print(f"{BLUE}5){RESET} {GREEN}Get AI Recommendations{RESET}")
        print(f"{BLUE}6){RESET} {GREEN}Exit{RESET}")
        
        try:
            choice = int(input(f"\n{CYAN}Enter your choice (1-6): {RESET}"))
            if choice == 1:
                infra_scanner()
            elif choice == 2:
                web_scanner()
            elif choice == 3:
                run_bandit_scan()
            elif choice == 4:
                view_logs()
            elif choice == 5:
                run_ai_recommendations()
            elif choice == 6:
                print(f"{GREEN}Exiting...{RESET}")
                break
            else:
                print(f"{RED}Invalid choice. Please select between 1-6.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a numeric value.{RESET}")

if __name__ == "__main__":
    main()
