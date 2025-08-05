import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSlider, QCheckBox, QGroupBox,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QCoreApplication

# --- Import custom modules ---
# Ensure these files are in the same directory or in the python path
from device_manager import DeviceManager
from audio_pipeline import AudioPipeline

class SuperHearingApp(QMainWindow):
    """
    The main application window for SuperHearing-X.
    It provides a GUI to control the audio pipeline and manage presets.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperHearing-X")
        self.setGeometry(100, 100, 500, 450) # Increased height for new buttons

        # --- Initialize backend components ---
        self.device_manager = DeviceManager()
        self.audio_pipeline = None

        # --- Store device info ---
        self.input_devices = self.device_manager.get_input_devices()
        self.output_devices = self.device_manager.get_output_devices()

        # --- Initialize UI ---
        self.initUI()
        
        # Set a flag to check if we are exiting
        self._is_exiting = False

    def initUI(self):
        """Sets up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Device Selection Group ---
        device_group = QGroupBox("Audio Devices")
        device_layout = QVBoxLayout()
        
        self.input_combo = QComboBox()
        self.input_combo.addItems(self.input_devices.values())
        default_input_idx = self.device_manager.get_default_input_device_index()
        if default_input_idx in self.input_devices:
            self.input_combo.setCurrentText(self.input_devices[default_input_idx])
        
        self.output_combo = QComboBox()
        self.output_combo.addItems(self.output_devices.values())
        default_output_idx = self.device_manager.get_default_output_device_index()
        if default_output_idx in self.output_devices:
            self.output_combo.setCurrentText(self.output_devices[default_output_idx])

        device_layout.addWidget(QLabel("Input Microphone:"))
        device_layout.addWidget(self.input_combo)
        device_layout.addWidget(QLabel("Output Headphones/Speakers:"))
        device_layout.addWidget(self.output_combo)
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)

        # --- Main Controls ---
        control_layout = QHBoxLayout()
        self.listen_button = QPushButton("Start Listening")
        self.listen_button.setCheckable(True)
        self.listen_button.clicked.connect(self.toggle_listening)
        control_layout.addWidget(self.listen_button)

        self.record_button = QPushButton("Record")
        self.record_button.setCheckable(True)
        self.record_button.setEnabled(False) 
        self.record_button.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_button)
        main_layout.addLayout(control_layout)

        # --- Enhancements Group ---
        enhancements_group = QGroupBox("Audio Enhancements")
        enhancements_layout = QVBoxLayout()

        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("Gain (dB):"))
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 40)
        self.gain_slider.setValue(10)
        self.gain_slider.valueChanged.connect(self.update_gain)
        self.gain_label = QLabel(f"{self.gain_slider.value()} dB")
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_label)
        enhancements_layout.addLayout(gain_layout)

        self.whisper_boost_checkbox = QCheckBox("Enable Whisper Boost")
        self.whisper_boost_checkbox.toggled.connect(self.update_whisper_boost)
        enhancements_layout.addWidget(self.whisper_boost_checkbox)
        
        enhancements_group.setLayout(enhancements_layout)
        main_layout.addWidget(enhancements_group)

        # --- Preset Management ---
        preset_group = QGroupBox("Presets")
        preset_layout = QHBoxLayout()
        self.load_preset_button = QPushButton("Load Preset")
        self.load_preset_button.clicked.connect(self.load_preset)
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.load_preset_button)
        preset_layout.addWidget(self.save_preset_button)
        preset_group.setLayout(preset_layout)
        main_layout.addWidget(preset_group)

        # --- Status Bar ---
        self.status_label = QLabel("Status: Stopped")
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

    def toggle_listening(self):
        """Starts or stops the audio pipeline."""
        if self.listen_button.isChecked():
            try:
                selected_input_name = self.input_combo.currentText()
                selected_output_name = self.output_combo.currentText()
                
                input_idx = next(k for k, v in self.input_devices.items() if v == selected_input_name)
                output_idx = next(k for k, v in self.output_devices.items() if v == selected_output_name)

                self.audio_pipeline = AudioPipeline(input_idx, output_idx)
                self.apply_current_settings_to_pipeline()
                self.audio_pipeline.start()
                
                if not self.audio_pipeline.is_running:
                    raise RuntimeError("Failed to start audio stream. Check console for errors.")

                self.listen_button.setText("Stop Listening")
                self.status_label.setText("Status: Listening")
                self.record_button.setEnabled(True)
                self.input_combo.setEnabled(False)
                self.output_combo.setEnabled(False)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not start audio stream:\n{e}")
                self.listen_button.setChecked(False)
                self.audio_pipeline = None
        else:
            if self.audio_pipeline:
                self.audio_pipeline.stop()
                self.audio_pipeline = None
            
            self.listen_button.setText("Start Listening")
            self.status_label.setText("Status: Stopped")
            self.record_button.setEnabled(False)
            self.record_button.setChecked(False)
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)

    def toggle_recording(self):
        """Starts or stops recording the audio."""
        if self.record_button.isChecked():
            if self.audio_pipeline:
                self.audio_pipeline.start_recording()
                self.record_button.setText("Stop Recording")
                self.status_label.setText("Status: Recording...")
        else:
            if self.audio_pipeline:
                self.audio_pipeline.stop_recording()
                self.record_button.setText("Record")
                self.status_label.setText("Status: Listening")

    def update_gain(self):
        gain_val = self.gain_slider.value()
        self.gain_label.setText(f"{gain_val} dB")
        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.gain_db = float(gain_val)

    def update_whisper_boost(self):
        is_enabled = self.whisper_boost_checkbox.isChecked()
        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.whisper_boost_enabled = is_enabled

    def apply_current_settings_to_pipeline(self):
        """Applies all GUI settings to the audio pipeline instance."""
        self.update_gain()
        self.update_whisper_boost()

    def load_preset(self):
        """Opens a file dialog to load a JSON preset file."""
        presets_dir = 'presets'
        os.makedirs(presets_dir, exist_ok=True)
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Preset", presets_dir, "JSON Files (*.json)", options=options)
        if fileName:
            try:
                with open(fileName, 'r') as f:
                    settings = json.load(f)
                self.apply_settings_from_preset(settings)
                QMessageBox.information(self, "Success", f"Preset '{os.path.basename(fileName)}' loaded.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load preset file:\n{e}")

    def save_preset(self):
        """Opens a file dialog to save the current settings to a JSON preset file."""
        presets_dir = 'presets'
        os.makedirs(presets_dir, exist_ok=True)
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Preset", presets_dir, "JSON Files (*.json)", options=options)
        if fileName:
            # Ensure the filename ends with .json
            if not fileName.endswith('.json'):
                fileName += '.json'
            
            current_settings = {
                "gain_db": self.gain_slider.value(),
                "whisper_boost_enabled": self.whisper_boost_checkbox.isChecked(),
                # Add other settings here as they are implemented (e.g., filters)
            }
            
            try:
                with open(fileName, 'w') as f:
                    json.dump(current_settings, f, indent=4)
                QMessageBox.information(self, "Success", f"Preset saved to '{os.path.basename(fileName)}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save preset file:\n{e}")

    def apply_settings_from_preset(self, settings):
        """Applies settings from a loaded preset to the GUI and pipeline."""
        self.gain_slider.setValue(settings.get("gain_db", 10))
        self.whisper_boost_checkbox.setChecked(settings.get("whisper_boost_enabled", False))
        
        # This will automatically update the pipeline if it's running
        self.apply_current_settings_to_pipeline()

    def closeEvent(self, event):
        """Ensures the audio stream is stopped when the app closes."""
        self._is_exiting = True
        if self.audio_pipeline and self.audio_pipeline.is_running:
            print("Closing: Stopping audio pipeline...")
            self.audio_pipeline.stop()
        event.accept()

if __name__ == '__main__':
    for directory in ['recordings', 'presets']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    app = QApplication(sys.argv)
    main_win = SuperHearingApp()
    main_win.show()
    sys.exit(app.exec_())
