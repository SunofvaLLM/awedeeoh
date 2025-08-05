Awedeeoh: Real-Time Audio Enhancement Suite
Awedeeoh is a professional-grade, real-time audio processing application that functions as a "software hearing aid on steroids." It captures audio from any microphone, passes it through a sophisticated digital signal processing (DSP) pipeline, and outputs the enhanced result to your headphones with minimal latency.

Quick Install & Run
macOS / Linux

git clone [https://github.com/SunofvaLLM/awedeeoh.git](https://github.com/SunofvaLLM/awedeeoh.git) && cd awedeeoh && chmod +x install.sh && ./install.sh && python3 main.py

Windows (PowerShell, Admin)

git clone [https://github.com/SunofvaLLM/awedeeoh.git](https://github.com/SunofvaLLM/awedeeoh.git); cd awedeeoh; ./install.bat

After the installer finishes, run python main.py

Core Features
Feature

Description

Dynamic Range Compressor

Amplifies quiet sounds and tames loud ones. Fully tunable with Threshold, Ratio, Attack, and Release.

Live Audio Passthrough

Real-time mic-to-output with near-zero latency.

Speech Focus Filter

A band-pass filter that isolates human voice frequency ranges.

Save & Load Presets

Create .json profiles for various scenarios like "Whisper Boost", "Military Intercept", or "Hearing Accessibility".

Voice Control (NLP)

Control the app via offline voice commands using the Vosk engine.

Device Management

Select from any available input/output device (e.g., USB mic, Bluetooth headset).

Recording

Save the enhanced audio output directly to a .wav file.

Full GUI

Built-in PyQt5 interface with toggles, sliders, and device selectors.

Use Cases
Scenario

Description

Accessibility

A configurable hearing assistant for providing clarity in conversations.

Surveillance

Enhance faint environmental noise or detect whispers from a distance.

Wildlife Listening

Boost distant bird calls, animal sounds, or natural ambience.

Meetings

Improve comprehension in noisy rooms or with distant speakers.

Private Monitoring

Fine-tune audio input without relying on hardware volume controls.

Modules & Dependencies
PyQt5 – For the Graphical User Interface (GUI).

sounddevice / pyaudio – For live audio input/output streaming.

numpy, scipy – For audio signal processing (filtering, compression).

vosk – For offline voice command recognition (optional).

soundfile – For saving recordings to .wav format.

json – For loading and saving preset profiles.

Install all dependencies automatically by running the install.sh or install.bat script, or manually with:

pip install -r requirements.txt

File Structure
awedeeoh/
├── main.py                 # Launches the GUI and main application loop
├── audio_pipeline.py       # Core DSP functions: compression, filtering, gain
├── device_manager.py       # Handles detection of audio I/O devices
├── nlp_listener.py         # Manages voice recognition thread
├── presets/
│   ├── whisper_boost.json  # Example preset for whisper enhancement
│   └── ...                 # Other user-created presets
├── recordings/             # Default directory for saved .
