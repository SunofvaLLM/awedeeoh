import numpy as np
import time
import signal
import sys

from devices.device_manager import DeviceManager
from audio_processing import apply_amplification, apply_equalizer, apply_noise_reduction

# === Global Parameters ===
SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 1024

# === Runtime Variables ===
running = True

def handle_interrupt(signum, frame):
    global running
    print("\n🛑 Gracefully stopping...")
    running = False

# === Main Audio Processing Loop ===
def main():
    signal.signal(signal.SIGINT, handle_interrupt)  # Handle Ctrl+C

    print("🔊 Real-Time Audio Enhancement for Distant Sounds\n")

    # === STEP 1: Initialize Devices ===
    device_manager = DeviceManager()
    device_manager.list_devices()
    device_manager.choose_input_device()
    device_manager.choose_output_device()

    input_stream = device_manager.open_input_stream(rate=SAMPLE_RATE, frames_per_buffer=FRAMES_PER_BUFFER)
    output_stream = device_manager.open_output_stream(rate=SAMPLE_RATE, frames_per_buffer=FRAMES_PER_BUFFER)

    # === STEP 2: Ask for Audio Settings ===
    try:
        gain = float(input("\n🎚️ Amplification Gain (e.g., 5.0 - 15.0): ") or "10.0")
        low_freq = int(input("🎚️ Low Cut Frequency for EQ (Hz, e.g., 100): ") or "100")
        high_freq = int(input("🎚️ High Boost Frequency for EQ (Hz, e.g., 5000): ") or "5000")
        use_noise_reduction = input("🎚️ Enable Noise Reduction? (y/n): ").strip().lower() == "y"
    except Exception as e:
        print(f"❌ Invalid input: {e}")
        sys.exit(1)

    print("\n🚀 Starting audio processing...")
    print("🎧 Press Ctrl+C to stop.\n")

    # === STEP 3: Audio Processing Loop ===
    try:
        while running:
            # Read audio input
            try:
                data = input_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            except Exception as e:
                print(f"⚠️ Input error: {e}")
                continue

            # Apply processing
            if use_noise_reduction:
                audio_data = apply_noise_reduction(audio_data, SAMPLE_RATE)
            audio_data = apply_equalizer(audio_data, SAMPLE_RATE, low_freq, high_freq, gain)
            audio_data = apply_amplification(audio_data, gain)

            # Clip to prevent overflow
            audio_data = np.clip(audio_data, -32768, 32767)

            # Output
            try:
                output_stream.write(audio_data.astype(np.int16).tobytes())
            except Exception as e:
                print(f"⚠️ Output error: {e}")
                continue

    finally:
        print("\n🧹 Cleaning up audio resources...")
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        device_manager.terminate()
        print("✅ Audio processing finished.")

if __name__ == "__main__":
    main()
