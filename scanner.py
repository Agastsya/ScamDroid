import subprocess
import sys
import time
import os
import datetime
import webbrowser
from urllib.parse import urlparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"  

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

LOG_DIR = os.path.join(SCRIPT_DIR, "reports")
AI_LOG_DIR = os.path.join(SCRIPT_DIR, "aiReport")
AI_LOG_FILE = os.path.join(AI_LOG_DIR, "ai_report.txt") 
LOG_FILE = os.path.join(LOG_DIR, "scanner_file.txt")
HTML_LOG_FILE = os.path.join(LOG_DIR, "scanner_file.html")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AI_LOG_DIR, exist_ok=True)

def display_banner():
    banner = rf"""
{Color.RED}
███████╗ ██████╗ █████╗ ███╗   ███╗██████╗ ██████╗  ██████╗ ██╗██████╗ 
██╔════╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔═══██╗██║██╔══██╗
███████╗██║     ███████║██╔████╔██║██║  ██║██████╔╝██║   ██║██║██║  ██║
╚════██║██║     ██╔══██║██║╚██╔╝██║██║  ██║██╔══██╗██║   ██║██║██║  ██║
███████║╚██████╗██║  ██║██║ ╚═╝ ██║██████╔╝██║  ██║╚██████╔╝██║██████╔╝
╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝ 
{Color.CYAN}                                                              v0.0.1
{Color.YELLOW} [Vulnerability Scanner and AI-Based Patching Recommendation Tool]
{Color.RESET}
"""
    # Typewriter effect
    for line in banner.split('\n'):
        print(line)
        time.sleep(0.05) if not sys.platform.startswith('win') else None

def log_result(scan_type, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"[{timestamp}] {scan_type} Results:\n{result}\n\n")
    
    with open(HTML_LOG_FILE, "a") as html_log:
        html_log.write(f"<h2>{scan_type} Results ({timestamp})</h2><pre>{result}</pre><hr>")


def ai_log_result(scan_type, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AI_LOG_FILE, "a") as log:  # Fixed variable name
        log.write(f"[{timestamp}] {scan_type} Results:\n{result}\n\n")
    
    with open(HTML_LOG_FILE, "a") as html_log:
        html_log.write(f"<h2>{scan_type} Results ({timestamp})</h2><pre>{result}</pre><hr>")

def delete_logs():
    open(LOG_FILE, "w").close()

def view_ai_logs():  # New function to view AI logs
    print(f"{GREEN}Displaying AI log contents...{RESET}")
    try:
        if not os.path.exists(AI_LOG_FILE):
            print(f"{YELLOW}No AI logs found.{RESET}")
            return
            
        with open(AI_LOG_FILE, "r") as f:
            contents = f.read()
            print(f"{CYAN}AI Logs:\n{RESET}{contents}")
    except Exception as e:
        print(f"{RED}Error reading AI log file: {e}{RESET}")




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

    try:
        # Check if Lynis is installed
        subprocess.run(['lynis', '--version'],
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}ERROR: Lynis not found. Please install Lynis first.{RESET}")
        print("Installation instructions: https://cisofy.com/lynis/")
        return

    try:
        # Since the script runs as root, no need for sudo
        process = subprocess.Popen(
            ['lynis', 'audit', 'system', '--quick', '--no-colors'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )

        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line, end='')  # Print each line as it appears
            sys.stdout.flush()
            output_lines.append(line.strip())  # Store output for logging

        process.stdout.close()
        process.wait()

        # Combine output and log it
        output = "\n".join(output_lines)
        print(f"{CYAN}Lynis audit completed. Saving results...{RESET}")
        log_result("Lynis Audit", output)

    except subprocess.TimeoutExpired:
        print(f"{RED}ERROR: Lynis scan timed out after 10 minutes{RESET}")
    except Exception as e:
        print(f"{RED}Error running Lynis scan: {str(e)}{RESET}")



def run_naabu_scanner(target_ip):
    print(f"{GREEN}Running Naabu scan on {target_ip}...{RESET}")
    try:
        # Replace '/usr/local/bin/naabu' with the correct path if needed
        result = subprocess.run(['/home/agastsya-joshi/go/bin/naabu', '-host', target_ip],
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
            ['python3', os.path.join(SCRIPT_DIR, "aiRecommendation.py")],
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
        print(f"{BLUE}(1){RESET} {GREEN}Scan multiple IPs using Nmap{RESET}")
        print(f"{BLUE}(2){RESET} {GREEN}Run Lynis scan{RESET}")
        print(f"{BLUE}(3){RESET} {GREEN}Scan multiple IPs using Naabu{RESET}")
        print(f"{BLUE}(4){RESET} {GREEN}Back to Main Menu{RESET}")
        
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
    display_banner()
    if os.geteuid() != 0:
        print(f"{RED}This script requires root privileges. Please run with 'sudo'.{RESET}")
        sys.exit(1)
    
    while True:
        print(f"\n{YELLOW}Main Menu:{RESET}")
        print(f"{BLUE}(1){RESET} {GREEN}Infrastructure Scanners{RESET}")
        print(f"{BLUE}(2){RESET} {GREEN}Web Scanner (Gobuster){RESET}")
        print(f"{BLUE}(3){RESET} {GREEN}Bandit Scanner{RESET}")
        print(f"{BLUE}(4){RESET} {GREEN}View Logs{RESET}")
        print(f"{BLUE}(5){RESET} {GREEN}View AI Logs{RESET}")
        print(f"{BLUE}(6){RESET} {GREEN}Get AI Recommendations{RESET}")
        print(f"{BLUE}(7){RESET} {GREEN}Exit{RESET}")
        
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
                view_ai_logs()
            elif choice == 6:
                run_ai_recommendations()
            elif choice == 0:
                delete_logs()
            elif choice == 7:
                print(f"{GREEN}Exiting...{RESET}")
                break
            else:
                print(f"{RED}Invalid choice. Please select between 1-6.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a numeric value.{RESET}")

if __name__ == "__main__":
    main()
