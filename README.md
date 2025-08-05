# Awedeeoh

**Real-Time Audio Enhancement and Processing Suite**

---

## What is Awedeeoh?

Awedeeoh is a chimichanga-grade, real-time audio processing application that functions as a "software hearing aid on steroids." It captures audio from any microphone, passes it through a sophisticated digital signal processing (DSP) pipeline, and outputs the enhanced result to your headphones with minimal latency. This allows you to amplify, isolate, and clarify sounds in your environment far beyond the capabilities of normal hearing.

The application is built with a graphical interface (GUI) and can be controlled with voice commands, making its powerful features accessible for a wide range of applications, from accessibility to professional audio monitoring.

---

## Quick Setup & Run (One-Liner)

For a fast setup, open your terminal (macOS/Linux) or PowerShell as Administrator (Windows) and run the appropriate command. **Note:** Replace `your-username` with your actual GitHub username if you fork the project.

**macOS / Linux:**
```bash
git clone [https://github.com/your-username/awedeeoh.git](https://github.com/SunofvaLLM/awedeeoh.git) && cd awedeeoh && chmod +x install.sh && ./install.sh && python3 main.py


Windows (run in PowerShell as Administrator):

git clone [https://github.com/your-username/awedeeoh.git](https://github.com/SunofvaLLM/awedeeoh.git); cd awedeeoh; ./install.bat

(After the installer finishes, run python main.py)

Core Features
Advanced Dynamic Range Compressor: The heart of the application. This isn't just a volume booster; it intelligently amplifies extremely quiet sounds while taming loud ones. With full control over Threshold, Ratio, Attack, and Release, you can fine-tune the audio to pull whispers out of a noisy room.

Live Audio Passthrough: Hear your microphone's input in real-time through your chosen output device with near-zero latency.

Speech Focus Filter: A specialized band-pass filter designed to isolate the typical frequencies of human speech, helping to clarify conversations and reduce background noise.

Save/Load Presets: Create and save your custom audio enhancement profiles as .json files. Switch between configurations for different scenarios instantly.

Voice Control (NLP): Using the offline vosk engine, you can control the application's core functions hands-free with commands like "start listening" or "load indoor preset."

Audio Recording: Save the fully enhanced audio output directly to a .wav file for later analysis or sharing.

Device Management: Automatically detects and allows you to select from all available input (microphones) and output (headphones/speakers) devices connected to your system.

Use Cases & Applications
Awedeeoh is a versatile tool designed for a variety of applications:

Accessibility & Hearing Assistance: Can be used as a powerful, configurable hearing aid to enhance conversations and environmental sounds for individuals with hearing loss.

Security & Surveillance: Monitor environments for faint sounds, listen for distant conversations, or enhance audio from security microphones.

Fieldwork & Nature Observation: Amplify the subtle sounds of wildlife for research or hobbyist purposes, like listening for distant bird calls or animal movements.

Paranormal Investigation: Use extreme sensitivity presets to listen for Electronic Voice Phenomena (EVP) and other unexplained sounds.

Personal Amplification: Overcome noisy environments like restaurants or public transport by focusing on the sounds you want to hear.

Manual Setup Instructions
If you prefer to set up the project manually, follow these steps.

1. Clone the Repository
First, clone this repository to your local machine.

git clone [https://github.com/your-username/awedeeoh.git](https://github.com/your-username/awedeeoh.git)
cd awedeeoh

2. Run the Installer
Run the appropriate installer for your operating system. This will install Python and all required libraries.

macOS / Linux:
Make the script executable, then run it.

chmod +x install.sh
./install.sh

Windows:
Right-click install.bat and select "Run as administrator".

3. Run the Application
Once the installation is complete, you can start the application.

python3 main.py
