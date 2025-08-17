# LameHug Malware Simulation 🛡️

![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)

LameHug is a Python-based script designed for **educational purposes** to simulate malicious behavior in a controlled environment. This project emulates a malware system, including a malicious Python script (`Fake-LameHug.py`), a Command-and-Control (C2) server, and integration with a Large Language Model (LLM). It draws inspiration from real-world malware techniques, such as those discussed in the article ["Art28 Attacks Security and Defense Sector Using AI-Based Software"](https://cip.gov.ua/en/news/art28-atakuye-sektor-bezpeki-ta-oboroni-za-dopomogoyu-programnogo-zasobu-sho-vikoristovuye-shtuchnii-intelekt?utm_medium=email&_hsenc=p2ANqtz-8yk0kLEjO6bhFzw_7MYh0ECEbbFldrVQ46uzL2dfzmJrJkCUlRG_hw1o9MEUsA5ftc_6jXzOnmMwOxfgitUC8nHYSwQGFS1eSPmI5luJr65NVwQM8&_hsmi=113619842&utm_content=113619842&utm_source=hs_email).

> **⚠️ Important**: This project is strictly for educational and testing purposes in controlled environments and must comply with all applicable laws and ethical guidelines.

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation and Usage](#installation-and-usage)
- [Project Components](#project-components)
- [Security and Ethical Considerations](#security-and-ethical-considerations)
- [Contributing](#contributing)
- [License](#license)

## Introduction
LameHug simulates a malware system comprising a Python script, a C2 server, and an LLM integration. The project is designed to help researchers and developers understand malware workflows in a safe, controlled setting.

## Prerequisites
To run the LameHug simulation, ensure you have the following:
- **Python 3.8+**
- **Ollama** (for LLM integration)
- **pip** (Python package manager)
- A configured **Command-and-Control (C2) server** environment

## Installation and Usage

1. **Install Ollama and Pull the LLM Model**  
   Install [Ollama](https://ollama.ai/) following the official documentation. Then, pull the `qwen2.5-coder:32b` model:
   ```bash
   ollama pull qwen2.5-coder:32b
   ```

2. **Install Python Dependencies**  
   Navigate to the project directory and install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `requirements.txt` includes packages like `flask`, `werkzeug`, and `langgraph`.

3. **Configure the C2 Server IP**  
   Update the IP address or hostname in the `Fake-LameHug.py` script and C2 server configuration to match your environment.

4. **Configure the Goals File**  
   Create or modify `goal.txt` in the project directory to define objectives for the script. The script reads this file line by line and passes each goal to the LLM. Example `goal.txt`:
   ```plaintext
   # goal.txt
   1. collect system information
   2. collect username
   ```

5. **Run the Python Script**  
   Start the simulation by running:
   ```bash
   python3 C2-Server.py
   python3 Fake-LameHug.py
   ```
   Ensure the C2 server is active and `goal.txt` is configured before execution.

## Project Components
- **LameHug Script (`Fake-LameHug.py`)**: A Python script built with [LangGraph] to simulate malicious tasks, such as connecting to the C2 server and processing goals from `goal.txt`.
- **C2 Server**: A Flask-based server handling file uploads and communication.
- **LLM Integration**: Utilizes the `qwen2.5-coder:32b` model via Ollama for AI-driven functionality.

## Security and Ethical Considerations
🚨 This project is for **educational and research purposes only** in a controlled, authorized environment. Unauthorized use to harm systems or networks is strictly prohibited and may violate applicable laws. Always adhere to legal and ethical standards.

## Contributing
Contributions are welcome! 🙌 Please submit a pull request or open an issue on the [project repository](https://github.com/your-repo/lamehug) for suggestions or improvements.

## License
This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.
