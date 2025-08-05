import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSlider, QCheckBox, QGroupBox,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSlot

# --- Import custom modules ---
from device_manager import DeviceManager
from audio_pipeline import AudioPipeline
from nlp_listener import NLPListener

class SuperHearingApp(QMainWindow):
    """
    The main application window for SuperHearing-X, fully aligned with the
    advanced audio pipeline, including compressor and limiter controls.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperHearing-X")
        self.setGeometry(100, 100, 550, 650) # Increased height for new controls

        self.device_manager = DeviceManager()
        self.audio_pipeline = None
        self.nlp_listener = None

        self.input_devices = self.device_manager.get_input_devices()
        self.output_devices = self.device_manager.get_output_devices()

        self.initUI()
        self._is_exiting = False

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Device Selection ---
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

        # --- Super Hearing Controls ---
        super_hearing_group = QGroupBox("Super Hearing Compressor")
        super_hearing_layout = QVBoxLayout()

        # Compressor Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold (dB):"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(-80, 0)
        self.threshold_slider.setValue(-50)
        self.threshold_slider.valueChanged.connect(self.update_super_hearing_settings)
        self.threshold_label = QLabel(f"{self.threshold_slider.value()} dB")
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        super_hearing_layout.addLayout(threshold_layout)

        # Compressor Ratio
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("Ratio:"))
        self.ratio_slider = QSlider(Qt.Horizontal)
        self.ratio_slider.setRange(1, 20)
        self.ratio_slider.setValue(8)
        self.ratio_slider.valueChanged.connect(self.update_super_hearing_settings)
        self.ratio_label = QLabel(f"{self.ratio_slider.value()}:1")
        ratio_layout.addWidget(self.ratio_slider)
        ratio_layout.addWidget(self.ratio_label)
        super_hearing_layout.addLayout(ratio_layout)

        # Compressor Attack
        attack_layout = QHBoxLayout()
        attack_layout.addWidget(QLabel("Attack (ms):"))
        self.attack_slider = QSlider(Qt.Horizontal)
        self.attack_slider.setRange(1, 100)
        self.attack_slider.setValue(5)
        self.attack_slider.valueChanged.connect(self.update_super_hearing_settings)
        self.attack_label = QLabel(f"{self.attack_slider.value()} ms")
        attack_layout.addWidget(self.attack_slider)
        attack_layout.addWidget(self.attack_label)
        super_hearing_layout.addLayout(attack_layout)

        # Compressor Release
        release_layout = QHBoxLayout()
        release_layout.addWidget(QLabel("Release (ms):"))
        self.release_slider = QSlider(Qt.Horizontal)
        self.release_slider.setRange(10, 500)
        self.release_slider.setValue(100)
        self.release_slider.valueChanged.connect(self.update_super_hearing_settings)
        self.release_label = QLabel(f"{self.release_slider.value()} ms")
        release_layout.addWidget(self.release_slider)
        release_layout.addWidget(self.release_label)
        super_hearing_layout.addLayout(release_layout)
        
        # Speech Focus
        self.speech_focus_checkbox = QCheckBox("Enable Speech Focus (300-3400Hz Filter)")
        self.speech_focus_checkbox.toggled.connect(self.update_super_hearing_settings)
        super_hearing_layout.addWidget(self.speech_focus_checkbox)
        
        super_hearing_group.setLayout(super_hearing_layout)
        main_layout.addWidget(super_hearing_group)

        # --- Final Output Controls ---
        output_group = QGroupBox("Final Output Controls")
        output_layout = QVBoxLayout()
        
        # General Gain
        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("Makeup Gain (dB):"))
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 40)
        self.gain_slider.setValue(10)
        self.gain_slider.valueChanged.connect(self.update_gain)
        self.gain_label = QLabel(f"{self.gain_slider.value()} dB")
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_label)
        output_layout.addLayout(gain_layout)

        # Limiter
        limiter_layout = QHBoxLayout()
        self.limiter_checkbox = QCheckBox("Enable Brickwall Limiter")
        self.limiter_checkbox.setChecked(True)
        self.limiter_checkbox.toggled.connect(self.update_super_hearing_settings)
        limiter_layout.addWidget(self.limiter_checkbox)
        output_layout.addLayout(limiter_layout)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # --- Presets & Voice Control ---
        bottom_controls_layout = QHBoxLayout()
        preset_group = QGroupBox("Presets")
        preset_layout = QHBoxLayout()
        self.load_preset_button = QPushButton("Load")
        self.load_preset_button.clicked.connect(self.load_preset)
        self.save_preset_button = QPushButton("Save")
        self.save_preset_button.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.load_preset_button)
        preset_layout.addWidget(self.save_preset_button)
        
        nlp_group = QGroupBox("Voice")
        nlp_layout = QHBoxLayout()
        self.nlp_toggle_checkbox = QCheckBox("On/Off")
        self.nlp_toggle_checkbox.toggled.connect(self.toggle_nlp_listener)
        nlp_layout.addWidget(self.nlp_toggle_checkbox)
        
        bottom_controls_layout.addWidget(preset_group)
        bottom_controls_layout.addWidget(nlp_group)
        main_layout.addLayout(bottom_controls_layout)

        self.status_label = QLabel("Status: Stopped")
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

    def update_gain(self):
        gain_val = self.gain_slider.value()
        self.gain_label.setText(f"{gain_val} dB")
        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.gain_db = float(gain_val)
    
    def update_super_hearing_settings(self):
        """Updates all advanced settings in the audio pipeline."""
        threshold_val = self.threshold_slider.value()
        self.threshold_label.setText(f"{threshold_val} dB")
        
        ratio_val = self.ratio_slider.value()
        self.ratio_label.setText(f"{ratio_val}:1")

        attack_val = self.attack_slider.value()
        self.attack_label.setText(f"{attack_val} ms")

        release_val = self.release_slider.value()
        self.release_label.setText(f"{release_val} ms")

        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.compressor_threshold_db = float(threshold_val)
                self.audio_pipeline.compressor_ratio = float(ratio_val)
                self.audio_pipeline.compressor_attack_ms = float(attack_val)
                self.audio_pipeline.compressor_release_ms = float(release_val)
                self.audio_pipeline.speech_focus_enabled = self.speech_focus_checkbox.isChecked()
                self.audio_pipeline.limiter_enabled = self.limiter_checkbox.isChecked()
    
    def apply_current_settings_to_pipeline(self):
        """Applies all GUI settings to the audio pipeline instance."""
        self.update_gain()
        self.update_super_hearing_settings()

    def toggle_listening(self):
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
                    raise RuntimeError("Failed to start audio stream.")

                self.listen_button.setText("Stop Listening")
                self.status_label.setText("Status: Listening")
                self.record_button.setEnabled(True)
                self.input_combo.setEnabled(False)
                self.output_combo.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not start audio stream:\n{e}")
                self.listen_button.setChecked(False)
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

    def save_preset(self):
        presets_dir = 'presets'
        os.makedirs(presets_dir, exist_ok=True)
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Preset", presets_dir, "JSON Files (*.json)")
        if fileName:
            if not fileName.endswith('.json'): fileName += '.json'
            settings = {
                "gain_db": self.gain_slider.value(),
                "compressor_threshold_db": self.threshold_slider.value(),
                "compressor_ratio": self.ratio_slider.value(),
                "compressor_attack_ms": self.attack_slider.value(),
                "compressor_release_ms": self.release_slider.value(),
                "speech_focus_enabled": self.speech_focus_checkbox.isChecked(),
                "limiter_enabled": self.limiter_checkbox.isChecked(),
            }
            with open(fileName, 'w') as f: json.dump(settings, f, indent=4)
            QMessageBox.information(self, "Success", f"Preset saved to '{os.path.basename(fileName)}'.")

    def load_preset(self, filename=None):
        if not filename:
            presets_dir = 'presets'
            os.makedirs(presets_dir, exist_ok=True)
            filename, _ = QFileDialog.getOpenFileName(self, "Load Preset", presets_dir, "JSON Files (*.json)")
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f: settings = json.load(f)
            self.apply_settings_from_preset(settings)
            QMessageBox.information(self, "Success", f"Preset '{os.path.basename(filename)}' loaded.")

    def apply_settings_from_preset(self, settings):
        self.gain_slider.setValue(settings.get("gain_db", 10))
        self.threshold_slider.setValue(settings.get("compressor_threshold_db", -50))
        self.ratio_slider.setValue(settings.get("compressor_ratio", 8))
        self.attack_slider.setValue(settings.get("compressor_attack_ms", 5))
        self.release_slider.setValue(settings.get("compressor_release_ms", 100))
        self.speech_focus_checkbox.setChecked(settings.get("speech_focus_enabled", False))
        self.limiter_checkbox.setChecked(settings.get("limiter_enabled", True))
        self.apply_current_settings_to_pipeline()

    def closeEvent(self, event):
        self._is_exiting = True
        if self.nlp_listener: self.nlp_listener.stop()
        if self.audio_pipeline: self.audio_pipeline.stop()
        event.accept()

    # --- Dummy/Placeholder methods for functions already implemented ---
    def toggle_recording(self):
        """Placeholder for recording logic."""
        if not self.audio_pipeline: return
        QMessageBox.information(self, "Recording", "Recording functionality is connected here.")

    def toggle_nlp_listener(self):
        """Placeholder for NLP logic."""
        if self.nlp_toggle_checkbox.isChecked():
            QMessageBox.information(self, "NLP", "Voice control would be activated here.")
        else:
            QMessageBox.information(self, "NLP", "Voice control would be deactivated here.")

    @pyqtSlot(str)
    def handle_voice_command(self, command):
        """Placeholder for handling voice commands."""
        print(f"Voice command received: {command}")


if __name__ == '__main__':
    for directory in ['recordings', 'presets', 'model']:
        if not os.path.exists(directory): os.makedirs(directory, exist_ok=True)
    app = QApplication(sys.argv)
    main_win = SuperHearingApp()
    main_win.show()
    sys.exit(app.exec_())
