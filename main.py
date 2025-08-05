import sys
import os
import asyncio
import websockets
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot

from device_manager import DeviceManager
from audio_pipeline import AudioPipeline
from nlp_listener import NLPListener

class WebSocketServer(QObject):
    """
    A WebSocket server that runs in a separate thread to handle
    communication with the web UI.
    """
    command_received = pyqtSignal(dict)
    
    def __init__(self, host='localhost', port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None

    async def handler(self, websocket, path):
        """Handles incoming WebSocket connections."""
        self.clients.add(websocket)
        print(f"Web client connected: {websocket.remote_address}")
        try:
            # Send initial device list upon connection
            self.command_received.emit({'action': 'get_devices'})
            async for message in websocket:
                data = json.loads(message)
                # print(f"Received from web UI: {data}") # Uncomment for debugging
                self.command_received.emit(data)
        except websockets.exceptions.ConnectionClosed:
            print(f"Web client disconnected: {websocket.remote_address}")
        finally:
            self.clients.remove(websocket)

    async def send_to_all(self, message):
        """Sends a message to all connected clients."""
        if self.clients:
            # Ensure message is a JSON string
            json_message = json.dumps(message)
            await asyncio.wait([client.send(json_message) for client in self.clients])

    def run(self):
    """Starts the WebSocket server in an event loop."""
    async def start_server():
        async with websockets.serve(self.handler, self.host, self.port):
            print(f"Starting WebSocket server on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    self.loop.run_until_complete(start_server())
    self.loop.run_forever()

class AwedeeohController(QObject):
    """
    Main controller for the Awedeeoh application.
    Manages the backend logic and communicates with the WebSocket server.
    """
    def __init__(self):
        super().__init__()
        self.device_manager = DeviceManager()
        self.audio_pipeline = None
        self.nlp_listener = None
        self.current_settings = {} 
        
        # WebSocket Server Setup
        self.ws_server = WebSocketServer()
        self.ws_thread = QThread()
        self.ws_server.moveToThread(self.ws_thread)
        self.ws_thread.started.connect(self.ws_server.run)
        self.ws_server.command_received.connect(self.handle_ws_command)
        self.ws_thread.start()

        # NLP Listener Setup
        self.nlp_thread = QThread()

    @pyqtSlot(dict)
    def handle_ws_command(self, data):
        """Processes commands received from the WebSocket server."""
        action = data.get('action')

        if action == 'get_devices':
            self.send_device_list()
        elif action == 'start_listening':
            self.current_settings.update(data)
            self.start_listening()
        elif action == 'stop_listening':
            self.stop_listening()
        elif action == 'update_settings':
            self.current_settings.update(data)
            self.update_pipeline_settings()
        elif action == 'start_recording':
            if self.audio_pipeline: self.audio_pipeline.start_recording()
        elif action == 'stop_recording':
            if self.audio_pipeline: self.audio_pipeline.stop_recording()
        elif action == 'load_preset':
            self.load_preset(data.get('preset_name'))
        elif action == 'toggle_voice_control':
            self.toggle_nlp_listener(data.get('enabled'))

    def send_message_to_ui(self, message):
        """Thread-safe method to send a message to the UI."""
        if self.ws_server.loop and self.ws_server.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.ws_server.send_to_all(message), self.ws_server.loop)

    def send_device_list(self):
        """Sends the list of audio devices to the web UI."""
        input_devices = self.device_manager.get_input_devices()
        output_devices = self.device_manager.get_output_devices()
        message = {
            'type': 'device_list',
            'input_devices': input_devices,
            'output_devices': output_devices
        }
        self.send_message_to_ui(message)
        
    def start_listening(self):
        """Starts the audio pipeline based on current settings."""
        if self.audio_pipeline and self.audio_pipeline.is_running: return
            
        try:
            input_idx = int(self.current_settings.get('input_device', -1))
            output_idx = int(self.current_settings.get('output_device', -1))

            if input_idx == -1 or output_idx == -1:
                print("Error: Input or output device not selected.")
                return

            self.audio_pipeline = AudioPipeline(input_idx, output_idx)
            self.update_pipeline_settings()
            self.audio_pipeline.start()
            self.send_status_update()
        except Exception as e:
            print(f"Error starting audio stream: {e}")

    def stop_listening(self):
        """Stops the audio pipeline."""
        if self.audio_pipeline:
            self.audio_pipeline.stop()
            self.audio_pipeline = None
        self.send_status_update()
        
    def update_pipeline_settings(self):
        """Updates the audio pipeline with new settings from the UI."""
        if not self.audio_pipeline or not self.current_settings: return

        with self.audio_pipeline.lock:
            # Map UI controls to pipeline attributes
            comp_settings = self.current_settings.get('compressor', {})
            self.audio_pipeline.compressor_threshold_db = float(comp_settings.get('threshold', -50))
            self.audio_pipeline.compressor_ratio = float(comp_settings.get('ratio', 8))
            self.audio_pipeline.compressor_attack_ms = float(comp_settings.get('attack', 5))
            self.audio_pipeline.compressor_release_ms = float(comp_settings.get('release', 100))
            
            # Note: The raw input/output volume is typically an OS-level setting.
            # We will use the "sensitivity" and "gain" sliders as pre- and post-pipeline gain stages.
            self.audio_pipeline.input_gain_db = float(self.current_settings.get('mic_sensitivity', 0))
            self.audio_pipeline.output_gain_db = float(self.current_settings.get('output_gain', 0))
            
            # The main "makeup_gain" is the final gain stage in the pipeline
            self.audio_pipeline.gain_db = float(self.current_settings.get('makeup_gain', 10))
            
            self.audio_pipeline.speech_focus_enabled = bool(self.current_settings.get('speech_focus', False))
            self.audio_pipeline.limiter_enabled = bool(self.current_settings.get('limiter', True))

    def load_preset(self, preset_name):
        """Loads a preset from a file, applies its settings, and updates the UI."""
        if not preset_name: return
        
        safe_name = preset_name.replace(" ", "_").lower()
        filename = f"presets/{safe_name}.json"
        
        if not os.path.exists(filename):
            print(f"Error: Preset file not found at {filename}")
            return

        try:
            with open(filename, 'r') as f:
                preset_settings = json.load(f)
            
            # Send the loaded settings to the UI so it can update the sliders/checkboxes
            message = {'type': 'settings_update', 'settings': preset_settings}
            self.send_message_to_ui(message)
            
            # Apply settings to the backend
            self.current_settings.update(preset_settings)
            self.update_pipeline_settings()
            print(f"Loaded preset: {preset_name}")

        except Exception as e:
            print(f"Error loading preset {preset_name}: {e}")

    def toggle_nlp_listener(self, enabled):
        """Starts or stops the NLP listener."""
        if enabled:
            if self.nlp_listener and self.nlp_listener.is_running: return
            
            input_idx = int(self.current_settings.get('input_device', -1))
            if input_idx == -1:
                print("Cannot start voice control without a selected input device.")
                # Optionally send an error message back to the UI
                return

            self.nlp_listener = NLPListener(device_index=input_idx)
            self.nlp_listener.moveToThread(self.nlp_thread)
            self.nlp_thread.started.connect(self.nlp_listener.run)
            self.nlp_listener.command_recognized.connect(self.handle_voice_command)
            self.nlp_thread.start()
            print("Voice control activated.")
        else:
            if self.nlp_listener:
                self.nlp_listener.stop()
                self.nlp_thread.quit()
                self.nlp_thread.wait()
                self.nlp_listener = None
                print("Voice control deactivated.")

    @pyqtSlot(str)
    def handle_voice_command(self, command):
        """Translates a recognized voice command into a backend action."""
        print(f"Voice command received: '{command}'")
        # This logic mimics the original GUI app's voice commands
        if "start listening" in command and (not self.audio_pipeline or not self.audio_pipeline.is_running):
            self.start_listening()
        elif "stop listening" in command and self.audio_pipeline and self.audio_pipeline.is_running:
            self.stop_listening()
        elif "record" in command:
            if self.audio_pipeline: self.audio_pipeline.start_recording()
        elif "stop recording" in command:
            if self.audio_pipeline: self.audio_pipeline.stop_recording()
        elif "load" in command and "preset" in command:
            # Simple parsing, looks for a known preset name in the command
            presets = ["whisper", "military", "accessibility", "heartbeat", "paranormal"]
            for p in presets:
                if p in command:
                    self.load_preset(p)
                    break

    def send_status_update(self):
        """Sends the current listening status to the UI."""
        is_listening = self.audio_pipeline is not None and self.audio_pipeline.is_running
        message = {'type': 'status_update', 'is_listening': is_listening}
        self.send_message_to_ui(message)


if __name__ == '__main__':
    # We need a QApplication instance to run the QObject-based controller
    app = QApplication(sys.argv)
    controller = AwedeeohController()
    print("Awedeeoh backend controller is running. Open index.html in a browser.")
    sys.exit(app.exec_())
