import sounddevice as sd
import queue
import json
import threading
from PyQt5.QtCore import QObject, pyqtSignal

# --- Vosk Integration ---
# Vosk is an optional dependency. We'll try to import it and handle its absence.
try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    print("Warning: 'vosk' library not found. Voice control will be disabled.")
    print("Install it with: pip install vosk")
    Model = None # Set to None to indicate it's not available

class NLPListener(QObject, threading.Thread):
    """
    Listens for voice commands in a separate thread using Vosk.
    """
    # Signal to send recognized commands back to the main GUI thread
    command_recognized = pyqtSignal(str)

    def __init__(self, device_index, sample_rate=16000):
        super().__init__()
        self.device_index = device_index
        self.sample_rate = int(sample_rate)
        self.q = queue.Queue()
        self.is_running = False

        # --- Vosk Model Loading ---
        self.model = None
        if Model:
            # Check for model existence and download if necessary
            model_path = "model"
            import os, zipfile, requests
            if not os.path.exists(model_path):
                print("Vosk model not found. Downloading a small English model...")
                model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                try:
                    response = requests.get(model_url, stream=True)
                    with open("vosk-model.zip", "wb") as f:
                        f.write(response.content)
                    with zipfile.ZipFile("vosk-model.zip", 'r') as zip_ref:
                        zip_ref.extractall(".")
                    os.rename("vosk-model-small-en-us-0.15", model_path)
                    os.remove("vosk-model.zip")
                    print("Model downloaded and extracted successfully.")
                    self.model = Model(model_path)
                except Exception as e:
                    print(f"Error downloading or setting up Vosk model: {e}")
            else:
                self.model = Model(model_path)

    def _audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def run(self):
        """The main loop of the listener thread."""
        if not self.model:
            print("Cannot start NLP listener: Vosk model not loaded.")
            return

        self.is_running = True
        try:
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize=8000,
                                   device=self.device_index, dtype='int16',
                                   channels=1, callback=self._audio_callback):
                
                recognizer = KaldiRecognizer(self.model, self.sample_rate)
                print("NLP Listener started. Say a command.")
                
                while self.is_running:
                    data = self.q.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        command = result.get("text", "")
                        if command:
                            print(f"Vosk recognized: '{command}'")
                            # Emit the signal to the main thread
                            self.command_recognized.emit(command.strip())
        except Exception as e:
            print(f"Error in NLP Listener thread: {e}")
        
        print("NLP Listener stopped.")

    def stop(self):
        """Stops the listener thread."""
        self.is_running = False


