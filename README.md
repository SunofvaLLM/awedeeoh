# Awedeeoh: Real-Time Audio Enhancement Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Awedeeoh is a professional-grade, real-time audio processing application that functions as a "software hearing aid on steroids." It captures audio from any microphone and passes it through a sophisticated digital signal processing (DSP) pipeline—a series of advanced audio effects—to output a finely tuned, enhanced result to your headphones with minimal latency.

The application is built with a user-friendly graphical interface (GUI) and can be controlled with voice commands, making its powerful features accessible for a wide range of uses, from improving accessibility to professional audio monitoring and intelligence gathering.

---

## Table of Contents
- [Features](#features)
- [Use Cases](#use-cases)
- [Installation](#installation)
- [Usage](#usage)

---

## Features

- 🎤 **Live Audio Passthrough:** Hear your microphone's input in real-time through your chosen output device. This core function is optimized for near-zero latency, ensuring the audio you hear is perfectly synchronized with the world around you.
- 🔊 **Advanced Dynamic Range Compressor:** Intelligently amplifies extremely quiet sounds while taming loud ones. It provides full control over **Threshold, Ratio, Attack, and Release**, allowing you to precisely shape the audio. For example, a fast attack can catch the snap of a twig, while a slow release provides a more natural-sounding decay after a loud noise.
- 🗣️ **Speech Focus Filter:** A specialized band-pass filter designed to isolate the typical frequencies of human speech (roughly 300Hz to 3400Hz). By cutting out low-end rumble and high-end hiss, it can dramatically improve the clarity of conversations in noisy environments.
- 💾 **Custom Presets:** Save and load your custom audio enhancement profiles as `.json` files. This allows you to instantly switch between complex configurations tailored for different scenarios, such as moving from a quiet room to a busy street.
- 🤖 **Voice Control (NLP):** Utilizes the offline `vosk` engine to control core functions hands-free. This is ideal for situations where you need to make adjustments without being physically at the computer, such as during fieldwork or surveillance.
- 📼 **High-Quality Recording:** Save the fully enhanced audio output directly to a lossless `.wav` file. This is perfect for documenting events, analyzing specific sounds, or sharing your findings with others.
- 🎧 **Multi-Device Management:** Automatically detects and allows you to select from all available input (microphones) and output (headphones/speakers) devices. This provides the flexibility to use high-quality hardware, like a professional USB microphone paired with wireless Bluetooth headphones.

---

## Use Cases

- **Accessibility:** Functions as a powerful, configurable hearing aid to enhance conversations and environmental sounds. For individuals with hearing loss, this can mean the difference between hearing a muddle of noise and having a clear, intelligible conversation in a crowded restaurant.
- **Security & Surveillance:** Monitor environments for faint sounds that might indicate an intrusion or an emergency. Enhance audio from a security camera feed to identify the source of a distant noise or clarify a barely audible conversation.
- **Fieldwork & Nature Observation:** Amplify the subtle sounds of wildlife for research or hobbyist purposes. Isolate the specific call of a rare bird from the cacophony of a dense forest or track the faint rustle of an animal moving through undergrowth.
- **Paranormal Investigation:** Use extreme sensitivity presets to listen for Electronic Voice Phenomena (EVP). The tool is designed to capture and amplify potential voices or whispers that are often recorded at volumes too low for the human ear to detect on its own.
- **Personal Amplification:** Overcome noisy environments like restaurants or public transport. Tune out the drone of an airplane engine to focus on a podcast, or amplify a soft-spoken friend's voice across a loud table.

---

## Installation

You can install Awedeeoh using the automated one-liner or by following the manual steps.

### Quick Install (One-Liner)

For a streamlined setup, open your terminal (macOS/Linux) or an **Administrator PowerShell** (Windows) and run the appropriate command.

*Note: Replace `your-username` with your actual GitHub username if you have forked this project.*

**macOS / Linux**
```bash
git clone [https://github.com/your-username/awedeeoh.git](https://github.com/your-username/awedeeoh.git) && cd awedeeoh && chmod +x install.sh && ./install.sh

Windows (PowerShell as Administrator)

git clone [https://github.com/your-username/awedeeoh.git](https://github.com/your-username/awedeeoh.git); cd awedeeoh; ./install.bat

Manual Installation
If you prefer to set up the project step-by-step:

Clone the Repository

git clone [https://github.com/your-username/awedeeoh.git](https://github.com/your-username/awedeeoh.git)
cd awedeeoh

Run the Installer
Execute the appropriate installer for your operating system. This script will install Python (if needed) and all required libraries.

macOS / Linux: Make the script executable (chmod +x) and then run it.

chmod +x install.sh
./install.sh

Windows: Right-click install.bat and select "Run as administrator".

Usage
Once the installation is complete, you can start the application from your terminal. Navigate to the project directory and run:

python3 main.py
