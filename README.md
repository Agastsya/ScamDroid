<p align="center">
  <a href="https://drive.google.com/file/d/1tTuLA0cuMH0Sm5hiHb5Pwq-xheq7D55r/view?usp=drive_link">
    <img src="https://drive.google.com/uc?export=view&id=1tTuLA0cuMH0Sm5hiHb5Pwq-xheq7D55r" alt="Repository Logo">
  </a>
</p>

# ScamDroid - Vulnerability Scanner and AI-Based Patching Recommendation Tool

## Overview
ScanDroid is an advanced security scanning and vulnerability patching recommendation tool designed to help users detect vulnerabilities in their infrastructure and web applications. It integrates multiple scanning tools like **Nmap, Lynis, Naabu, Gobuster, and Bandit**, along with an AI-based recommendation engine to provide intelligent patching suggestions.

<p align="center">
  <img src="https://github.com/user-attachments/assets/73b7b1d6-b822-4a0a-b34e-e8ed34cb8f33" alt="Screenshot from 2025-03-21 00-36-00">
</p>

## Features
- **Infrastructure Scanning:** Uses Nmap, Lynis, and Naabu for network and system vulnerability detection.
- **Web Application Scanning:** Gobuster for directory enumeration.
- **Source Code Analysis:** Bandit for Python security analysis.
- **AI-Powered Patching Recommendations:** Utilizes Groq AI to analyze scan logs and suggest mitigations.
- **Detailed Reporting:** Generates log files in text and HTML formats for easy analysis.

## System Requirements
- **OS:** Linux (Tested on Kali Linux)
- **Dependencies:**
  - `python3`
  - `pandas`
  - `nmap`
  - `lynis`
  - `naabu`
  - `gobuster`
  - `bandit`
  - `requests`
- **API Key:** Groq API key for AI-based recommendations

## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/scandroid.git
   cd scandroid
   ```
2. **Install dependencies:**
   ```sh
   sudo apt install nmap lynis naabu gobuster bandit
   pip install pandas requests
   ```
3. **Set up API Key:**
   - Open `aiRecommendation.py`
   - Replace `{API_KEY}` with your actual Groq API key.

## Usage
### 1. Running the Scanner
```sh
sudo python3 scanner.py
```
- Select options from the menu to perform scans.
- Logs are saved at `/home/kali/Downloads/finalScanner/reports/`.

### 2. Running the CSV Extractor
```sh
python3 csvExtractor.py --source /path/to/logs --output_dir /path/to/output
```
- Extracts vulnerabilities from Lynis logs and generates CSV reports.

### 3. Running AI-Based Recommendations
```sh
python3 aiRecommendation.py
```
- Reads scan logs and provides AI-driven security recommendations.

## File Structure
```
scandroid/
├── scanner.py         # Main script for scanning
├── csvExtractor.py    # Extracts vulnerabilities from logs to CSV
├── aiRecommendation.py # AI-based patch recommendations
├── README.md          # Documentation
└── reports/           # Log files generated after scanning
```

## Logging and Reports
- **Plain text logs:** `/home/kali/Downloads/finalScanner/reports/scanner_file.txt`
- **HTML reports:** `/home/kali/Downloads/finalScanner/reports/scanner_file.html`
- **AI reports:** `/home/kali/Downloads/finalScanner/aiReport/ai_report.txt`

## Future Enhancements
- Add support for more vulnerability scanning tools.
- Implement automated patching.
- Enhance AI recommendations with additional machine learning models.

## Contributors
- **Agastsya Joshi** - Co-founder
- **Karman Arora** - Co-founder
- **Nitin Dogra** - Co-founder
- **Open to Contributions**



