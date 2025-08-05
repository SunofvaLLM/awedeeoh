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
    command_received = pyqtSignal(dict)

    def __init__(self, host='localhost', port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        print(f"Web client connected: {websocket.remote_address}")
        try:
            self.command_received.emit({'action': 'get_devices'})
            async for message in websocket:
                data = json.loads(message)
                self.command_received.emit(data)
        except websockets.exceptions.ConnectionClosed:
            print(f"Web client disconnected: {websocket.remote_address}")
        finally:
            self.clients.remove(websocket)

    async def send_to_all(self, message):
        if self.clients:
            json_message = json.dumps(message)
            await asyncio.gather(*(client.send(json_message) for client in self.clients))

    def run(self):
        async def start():
            async with websockets.serve(self.handler, self.host, self.port):
                print(f"Starting WebSocket server on ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(start())
        self.loop.run_forever()


class AwedeeohController(QObject):
    def __init__(self):
        super().__init__()
        self.device_manager = DeviceManager()
        self.audio_pipeline = None
        self.nlp_listener = None
        self.current_settings = {}

        # WebSocket setup
        self.ws_server = WebSocketServer()
        self.ws_thread = QThread()
        self.ws_server.moveToThread(self.ws_thread)
        self.ws_thread.started.connect(self.ws_server.run)
        self.ws_server.command_received.connect(self.handle_ws_command)
        self.ws_thread.start()

        # NLP thread
        self.nlp_thread = QThread()

    @pyqtSlot(dict)
    def handle_ws_command(self, data):
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
            if self.audio_pipeline:
                self.audio_pipeline.start_recording()
        elif action == 'stop_recording':
            if self.audio_pipeline:
                self.audio_pipeline.stop_recording()
        elif action == 'load_preset':
            self.load_preset(data.get('preset_name'))
        elif action == 'toggle_voice_control':
            self.toggle_nlp_listener(data.get('enabled'))

    def send_message_to_ui(self, message):
        if self.ws_server.loop and self.ws_server.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws_server.send_to_all(message),
                self.ws_server.loop
            )

    def send_device_list(self):
        input_devices = self.device_manager.get_input_devices()
        output_devices = self.device_manager.get_output_devices()
        self.send_message_to_ui({
            'type': 'device_list',
            'input_devices': input_devices,
            'output_devices': output_devices
        })

    def start_listening(self):
        if self.audio_pipeline and self.audio_pipeline.is_running:
            return

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
        if self.audio_pipeline:
            self.audio_pipeline.stop()
            self.audio_pipeline = None
        self.send_status_update()

    def update_pipeline_settings(self):
        if not self.audio_pipeline or not self.current_settings:
            return

        with self.audio_pipeline.lock:
            comp = self.current_settings.get('compressor', {})
            self.audio_pipeline.compressor_threshold_db = float(comp.get('threshold', -50))
            self.audio_pipeline.compressor_ratio = float(comp.get('ratio', 8))
            self.audio_pipeline.compressor_attack_ms = float(comp.get('attack', 5))
            self.audio_pipeline.compressor_release_ms = float(comp.get('release', 100))
            self.audio_pipeline.input_gain_db = float(self.current_settings.get('mic_sensitivity', 0))
            self.audio_pipeline.output_gain_db = float(self.current_settings.get('output_gain', 0))
            self.audio_pipeline.gain_db = float(self.current_settings.get('makeup_gain', 10))
            self.audio_pipeline.speech_focus_enabled = bool(self.current_settings.get('speech_focus', False))
            self.audio_pipeline.limiter_enabled = bool(self.current_settings.get('limiter', True))

    def load_preset(self, preset_name):
        if not preset_name:
            return

        safe_name = preset_name.replace(" ", "_").lower()
        preset_path = os.path.join("presets", f"{safe_name}.json")
        os.makedirs("presets", exist_ok=True)

        if not os.path.exists(preset_path):
            print(f"Error: Preset not found: {preset_path}")
            return

        try:
            with open(preset_path, 'r') as f:
                preset_settings = json.load(f)
            self.send_message_to_ui({'type': 'settings_update', 'settings': preset_settings})
            self.current_settings.update(preset_settings)
            self.update_pipeline_settings()
            print(f"Loaded preset: {preset_name}")
        except Exception as e:
            print(f"Error loading preset '{preset_name}': {e}")

    def toggle_nlp_listener(self, enabled):
        if enabled:
            if self.nlp_listener and self.nlp_listener.is_running:
                return
            input_idx = int(self.current_settings.get('input_device', -1))
            if input_idx == -1:
                print("Cannot start voice control without a selected input device.")
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
        print(f"Voice command received: '{command}'")
        if "start listening" in command and (not self.audio_pipeline or not self.audio_pipeline.is_running):
            self.start_listening()
        elif "stop listening" in command and self.audio_pipeline and self.audio_pipeline.is_running:
            self.stop_listening()
        elif "record" in command:
            if self.audio_pipeline:
                self.audio_pipeline.start_recording()
        elif "stop recording" in command:
            if self.audio_pipeline:
                self.audio_pipeline.stop_recording()
        elif "load" in command and "preset" in command:
            try:
                available = [f.split('.')[0] for f in os.listdir("presets") if f.endswith(".json")]
                for p in available:
                    if p in command:
                        self.load_preset(p)
                        break
            except Exception as e:
                print(f"Error scanning presets: {e}")

    def send_status_update(self):
        is_listening = self.audio_pipeline is not None and self.audio_pipeline.is_running
        self.send_message_to_ui({'type': 'status_update', 'is_listening': is_listening})

    def cleanup(self):
        self.stop_listening()
        if self.nlp_listener:
            self.toggle_nlp_listener(False)
        self.ws_thread.quit()
        self.ws_thread.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = AwedeeohController()
    print("Awedeeoh backend controller is running. Open index.html in a browser.")
    try:
        sys.exit(app.exec_())
    finally:
        controller.cleanup()
