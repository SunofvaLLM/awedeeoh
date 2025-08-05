import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import butter, lfilter
import threading
import queue

class AudioPipeline:
    """
    Manages the real-time audio processing pipeline with advanced "Super Hearing" features.
    This version includes multiple gain stages for fine-tuned control.
    """
    def __init__(self, input_device_index, output_device_index, sample_rate=44100, chunk_size=1024):
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        self.stream = None
        self.is_running = False
        self.lock = threading.Lock()

        # --- Multi-stage Gain Parameters ---
        self.input_gain_db = 0.0      # Pre-processing gain (Sensitivity)
        self.gain_db = 10.0           # Post-compressor makeup gain
        self.output_gain_db = 0.0     # Final output gain (Volume)

        # --- Super Hearing Parameters ---
        self.noise_gate_threshold = 0.01
        self.compressor_enabled = True
        self.compressor_threshold_db = -50.0
        self.compressor_ratio = 8.0
        self.compressor_attack_ms = 5.0
        self.compressor_release_ms = 100.0
        self._compressor_gain_reduction = 1.0 

        self.speech_focus_enabled = False
        self.band_pass_low_cutoff = 300.0
        self.band_pass_high_cutoff = 3400.0
        
        self.limiter_enabled = True
        self.limiter_threshold_db = -1.0

        # --- Recording State ---
        self.is_recording = False
        self.recording_queue = queue.Queue()
        self.recording_thread = None
        self.recording_filename = "recordings/captured.wav"

    def _audio_callback(self, indata, outdata, frames, time, status):
        """This function is called for each audio block."""
        if status:
            print(status)
        
        with self.lock:
            processed_data = self.process_frame(indata.copy())
            outdata[:] = processed_data
            
            if self.is_recording:
                self.recording_queue.put(processed_data.copy())

    def process_frame(self, data):
        """
        Applies all enabled audio enhancements to a frame in a specific order.
        """
        audio_data = data.astype(np.float32)

        # 1. Input Gain (Sensitivity)
        # Applied first to boost the raw signal before any processing.
        if self.input_gain_db != 0:
            audio_data *= 10**(self.input_gain_db / 20.0)

        # 2. Noise Gate
        if self.noise_gate_threshold > 0:
            audio_data[np.abs(audio_data) < self.noise_gate_threshold] = 0.0
        
        # 3. Speech Focus Filter (Band-pass)
        if self.speech_focus_enabled:
            audio_data = self._band_pass_filter(
                audio_data, 
                self.band_pass_low_cutoff, 
                self.band_pass_high_cutoff, 
                self.sample_rate
            )

        # 4. Super Hearing Compressor
        if self.compressor_enabled:
            audio_data = self._dynamic_range_compressor_stateful(audio_data)

        # 5. Makeup Gain
        # Applied after the compressor to make up for overall volume reduction.
        if self.gain_db != 0:
            audio_data *= 10**(self.gain_db / 20.0)
            
        # 6. Output Gain (Volume)
        # A final volume control before the limiter.
        if self.output_gain_db != 0:
            audio_data *= 10**(self.output_gain_db / 20.0)

        # 7. Brickwall Limiter (Final Stage)
        # Prevents clipping from all the previous gain stages.
        if self.limiter_enabled:
            audio_data = self._limiter(audio_data, self.limiter_threshold_db)

        # Final safety clamp
        np.clip(audio_data, -1.0, 1.0, out=audio_data)
        
        return audio_data

    def _dynamic_range_compressor_stateful(self, data):
        """Applies compression with attack and release times."""
        if self.compressor_ratio <= 1: return data

        attack_coeff = np.exp(-1.0 / (self.sample_rate * (self.compressor_attack_ms / 1000.0)))
        release_coeff = np.exp(-1.0 / (self.sample_rate * (self.compressor_release_ms / 1000.0)))
        threshold_linear = 10**(self.compressor_threshold_db / 20.0)
        processed_data = np.zeros_like(data)

        for i, sample in enumerate(data):
            if abs(sample) > threshold_linear:
                target_gain = (threshold_linear + (abs(sample) - threshold_linear) / self.compressor_ratio) / abs(sample)
                self._compressor_gain_reduction = (attack_coeff * self._compressor_gain_reduction) + (1 - attack_coeff) * target_gain
            else:
                self._compressor_gain_reduction = (release_coeff * self._compressor_gain_reduction) + (1 - release_coeff) * 1.0
            
            processed_data[i] = sample * self._compressor_gain_reduction
            
        return processed_data

    def _limiter(self, data, threshold_db):
        """Applies a hard brickwall limiter."""
        threshold_linear = 10**(threshold_db / 20.0)
        clipping_mask = np.abs(data) > threshold_linear
        data[clipping_mask] = np.sign(data[clipping_mask]) * threshold_linear
        return data

    def _band_pass_filter(self, data, lowcut, highcut, fs, order=5):
        """Applies a band-pass filter."""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = lfilter(b, a, data, axis=0)
        return y

    def start(self):
        """Starts the audio stream."""
        if self.is_running: return
        self.is_running = True
        try:
            self.stream = sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=(self.input_device_index, self.output_device_index),
                channels=1,
                dtype='float32',
                callback=self._audio_callback
            )
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_running = False

    def stop(self):
        """Stops the audio stream."""
        if not self.is_running: return
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_running = False
        self.stream = None
        if self.is_recording:
            self.stop_recording()

    def start_recording(self, filename="recordings/captured.wav"):
        """Starts recording the processed audio."""
        if self.is_recording: return
        self.recording_filename = filename
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._write_recording)
        self.recording_thread.start()

    def stop_recording(self):
        """Stops the recording and saves the file."""
        if not self.is_recording: return
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()

    def _write_recording(self):
        """Worker thread function to write audio data to a WAV file."""
        with sf.SoundFile(self.recording_filename, mode='w', samplerate=self.sample_rate, channels=1) as audio_file:
            while self.is_recording or not self.recording_queue.empty():
                try:
                    data = self.recording_queue.get(timeout=1)
                    audio_file.write(data)
                except queue.Empty:
                    if not self.is_recording:
                        break
