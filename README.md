# Awedeeoh: Real-Time Audio Enhancement Suite

**Awedeeoh** is a professional-grade real-time audio processing application—essentially a "software hearing aid on steroids." It captures microphone input, processes it through a digital signal pipeline, and outputs the enhanced audio to your headphones with near-zero latency.

---

##  Quick Install & Run

### macOS / Linux

```bash
git clone https://github.com/SunofvaLLM/awedeeoh.git && cd awedeeoh && chmod +x install.sh && ./install.sh && python3 main.py
```

### Windows (PowerShell, Run as Administrator)

```powershell
git clone https://github.com/SunofvaLLM/awedeeoh.git; cd awedeeoh; ./install.bat
```

Once installation completes, launch with:

```bash
python main.py
```

---

##  Core Features

| Feature                      | Description                                                                                                |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Dynamic Range Compressor** | Amplifies quiet sounds and controls loud peaks. Adjustable Threshold, Ratio, Attack, and Release settings. |
| **Live Audio Passthrough**   | Real-time microphone to output with extremely low latency.                                                 |
| **Speech Focus Filter**      | Band-pass filter optimized to isolate human voice frequencies.                                             |
| **Save & Load Presets**      | Store DSP settings as `.json` profiles (e.g., "Whisper Boost", "Military Intercept").                      |
| **Voice Control (NLP)**      | Optional offline control using the Vosk engine for speech recognition.                                     |
| **Device Management**        | Select input/output from all connected devices (USB mic, Bluetooth, etc.).                                 |
| **Recording**                | Save processed audio directly to `.wav` files.                                                             |
| **Full GUI**                 | PyQt5 interface with sliders, toggles, and device selectors.                                               |

---

##  Use Cases

| Scenario               | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| **Accessibility**      | Improves conversation clarity for users with hearing difficulty. |
| **Surveillance**       | Enhances faint or distant environmental sounds.                  |
| **Wildlife Listening** | Boosts distant animal sounds or natural ambience.                |
| **Meetings**           | Enhances voices in large rooms or noisy environments.            |
| **Private Monitoring** | Allows precise tuning without hardware gain changes.             |

---

##  Modules & Dependencies

* `PyQt5` – GUI interface
* `sounddevice` or `pyaudio` – Audio stream handling
* `numpy`, `scipy` – Signal processing functions
* `vosk` – Optional offline NLP voice control
* `soundfile` – Output `.wav` recording
* `json` – Preset save/load system

Install dependencies automatically:

```bash
./install.sh        # macOS/Linux
./install.bat       # Windows
```

Or manually:

```bash
pip install -r requirements.txt
```

---

##  File Structure

```awedeeoh/
│
├── main.py                 # Launches the GUI and main application loop
├── audio_pipeline.py       # Core DSP functions: compression, filtering, gain
├── device_manager.py       # Handles detection of audio I/O devices
├── nlp_listener.py         # Manages voice recognition thread
│
├── install.sh              # Installer script for macOS / Linux
├── install.bat             # Installer script for Windows
├── requirements.txt        # List of Python dependencies
├── README.md               # Project documentation (this file)
├── index.html              # Optional project webpage
│
├── presets/                # Directory for saved setting profiles
│   ├── whisper_boost.json
│   ├── heartbeat_detector.json
│   ├── military_intercept.json
│   ├── hearing_accessibility.json
│   ├── superhuman.json
│   ├── paw_steps.json
│   └── ...
│
├── recordings/             # Default directory for saved .wav files
│   └── (empty by default)
│
└── model/                  # Directory for the Vosk NLP model
    └── (empty by default)  # (Downloaded on first run of voice control)

--
