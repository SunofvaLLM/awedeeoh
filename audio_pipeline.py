import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QSlider, QCheckBox, QGroupBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, QCoreApplication

# --- Import custom modules ---
# Ensure these files are in the same directory or in the python path
from device_manager import DeviceManager
from audio_pipeline import AudioPipeline

class SuperHearingApp(QMainWindow):
    """
    The main application window for SuperHearing-X.
    It provides a GUI to control the audio pipeline.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperHearing-X")
        self.setGeometry(100, 100, 500, 400)

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
        
        # Input Device
        self.input_combo = QComboBox()
        self.input_combo.addItems(self.input_devices.values())
        default_input_idx = self.device_manager.get_default_input_device_index()
        if default_input_idx in self.input_devices:
            self.input_combo.setCurrentText(self.input_devices[default_input_idx])
        
        # Output Device
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
        self.record_button.setEnabled(False) # Disabled until listening starts
        self.record_button.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_button)
        main_layout.addLayout(control_layout)

        # --- Enhancements Group ---
        enhancements_group = QGroupBox("Audio Enhancements")
        enhancements_layout = QVBoxLayout()

        # Gain Slider
        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("Gain (dB):"))
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 40) # 0 to 40 dB
        self.gain_slider.setValue(10)
        self.gain_slider.valueChanged.connect(self.update_gain)
        self.gain_label = QLabel(f"{self.gain_slider.value()} dB")
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_label)
        enhancements_layout.addLayout(gain_layout)

        # Whisper Boost Checkbox
        self.whisper_boost_checkbox = QCheckBox("Enable Whisper Boost")
        self.whisper_boost_checkbox.toggled.connect(self.update_whisper_boost)
        enhancements_layout.addWidget(self.whisper_boost_checkbox)
        
        enhancements_group.setLayout(enhancements_layout)
        main_layout.addWidget(enhancements_group)

        # --- Status Bar ---
        self.status_label = QLabel("Status: Stopped")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

    def toggle_listening(self):
        """Starts or stops the audio pipeline."""
        if self.listen_button.isChecked():
            # --- Start Listening ---
            try:
                selected_input_name = self.input_combo.currentText()
                selected_output_name = self.output_combo.currentText()
                
                # Find the device index from its name
                input_idx = next(k for k, v in self.input_devices.items() if v == selected_input_name)
                output_idx = next(k for k, v in self.output_devices.items() if v == selected_output_name)

                self.audio_pipeline = AudioPipeline(input_idx, output_idx)
                
                # Apply current GUI settings to the new pipeline instance
                self.update_gain()
                self.update_whisper_boost()
                
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
            # --- Stop Listening ---
            if self.audio_pipeline:
                self.audio_pipeline.stop()
                self.audio_pipeline = None
            
            self.listen_button.setText("Start Listening")
            self.status_label.setText("Status: Stopped")
            self.record_button.setEnabled(False)
            self.record_button.setChecked(False) # Uncheck record button if it was on
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
        """Updates the gain in the audio pipeline."""
        gain_val = self.gain_slider.value()
        self.gain_label.setText(f"{gain_val} dB")
        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.gain_db = float(gain_val)

    def update_whisper_boost(self):
        """Updates the whisper boost setting in the pipeline."""
        is_enabled = self.whisper_boost_checkbox.isChecked()
        if self.audio_pipeline:
            with self.audio_pipeline.lock:
                self.audio_pipeline.whisper_boost_enabled = is_enabled
    
    def closeEvent(self, event):
        """Ensures the audio stream is stopped when the app closes."""
        self._is_exiting = True
        if self.audio_pipeline and self.audio_pipeline.is_running:
            print("Closing: Stopping audio pipeline...")
            self.audio_pipeline.stop()
        event.accept()


if __name__ == '__main__':
    # Ensure recordings directory exists
    if not os.path.exists('recordings'):
        os.makedirs('recordings')
        
    app = QApplication(sys.argv)
    main_win = SuperHearingApp()
    main_win.show()
    sys.exit(app.exec_())
