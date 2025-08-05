import numpy as np
import scipy.signal as signal
import noisereduce as nr
import argparse
import os

# Amplification function: Boosts volume by a specific gain factor.
def apply_amplification(audio_data, gain):
    """
    Amplify the audio by a specific gain factor.
    
    :param audio_data: Input audio signal (numpy array)
    :param gain: Gain factor to amplify the audio signal
    :return: Amplified audio signal (numpy array)
    """
    return audio_data * gain

# Equalization function: Boost mid and high frequencies for better speech clarity.
def apply_equalizer(audio_data, fs, low_freq=100, high_freq=5000, gain=10):
    """
    Apply an equalizer to boost mid and high frequencies for speech clarity.
    
    :param audio_data: Input audio signal (numpy array)
    :param fs: Sample rate of the audio signal
    :param low_freq: Lower frequency threshold for high-pass filter (Hz)
    :param high_freq: Upper frequency for boosting (Hz)
    :param gain: Gain value for boosting selected frequencies
    :return: Processed audio signal with EQ applied
    """
    nyquist = 0.5 * fs
    
    # High-pass filter to remove rumble below low_freq
    low = low_freq / nyquist
    b, a = signal.butter(1, low, btype='high')
    audio_data = signal.filtfilt(b, a, audio_data)
    
    # Band-pass filter to boost mid and high frequencies
    high = high_freq / nyquist
    b, a = signal.butter(1, [low, high], btype='band')
    boosted_audio = signal.filtfilt(b, a, audio_data) * gain
    
    return boosted_audio

# Noise reduction function: Reduce unwanted noise in the audio
def apply_noise_reduction(audio_data, sr):
    """
    Reduce background noise in the audio data using noisereduce library.
    
    :param audio_data: Input audio signal (numpy array)
    :param sr: Sample rate of the audio signal
    :return: Noise-reduced audio signal (numpy array)
    """
    return nr.reduce_noise(y=audio_data, sr=sr)

# Process audio based on user settings
def process_audio(input_file, output_file, gain, low_freq, high_freq, sr, reduce_noise):
    """
    Process the input audio file with amplification, EQ, and noise reduction.
    
    :param input_file: Path to the input audio file
    :param output_file: Path to save the processed audio file
    :param gain: Gain for amplification
    :param low_freq: Low frequency for equalizer
    :param high_freq: High frequency for equalizer
    :param sr: Sample rate
    :param reduce_noise: Flag to enable noise reduction
    """
    # Load audio file
    try:
        audio_data = np.fromfile(input_file, dtype=np.int16)  # Assuming 16-bit mono PCM for simplicity
    except Exception as e:
        print(f"Error loading file {input_file}: {e}")
        return

    # Apply noise reduction if enabled
    if reduce_noise:
        audio_data = apply_noise_reduction(audio_data, sr)

    # Apply equalizer to boost frequencies
    audio_data = apply_equalizer(audio_data, sr, low_freq, high_freq, gain)

    # Apply amplification
    audio_data = apply_amplification(audio_data, gain)

    # Save processed audio to output file
    try:
        audio_data.tofile(output_file)  # Save as raw PCM (for simplicity in this example)
        print(f"Processed audio saved to {output_file}")
    except Exception as e:
        print(f"Error saving file {output_file}: {e}")

# CLI Function for user interaction
def main():
    parser = argparse.ArgumentParser(description="Audio Processing Tool - Enhance quiet and distant sounds")
    
    # CLI Options
    parser.add_argument('input_file', type=str, help="Path to the input audio file")
    parser.add_argument('output_file', type=str, help="Path to save the processed audio file")
    
    parser.add_argument('--gain', type=float, default=10.0, help="Amplification gain for boosting audio volume")
    parser.add_argument('--low_freq', type=int, default=100, help="Low frequency for EQ (Hz), typically 100Hz for bass reduction")
    parser.add_argument('--high_freq', type=int, default=5000, help="High frequency for EQ (Hz), typically 5000Hz for clarity boost")
    parser.add_argument('--reduce_noise', action='store_true', help="Enable noise reduction")
    
    # Display the available options
    args = parser.parse_args()

    # Print help if no arguments are passed
    if not any(vars(args).values()):
        parser.print_help()
        return

    print(f"Processing {args.input_file} -> {args.output_file}")
    print(f"Gain: {args.gain} | EQ: {args.low_freq}Hz - {args.high_freq}Hz | Noise Reduction: {'Enabled' if args.reduce_noise else 'Disabled'}")

    # Process the audio
    sr = 44100  # Default sample rate (can be detected dynamically from audio file if needed)
    process_audio(args.input_file, args.output_file, args.gain, args.low_freq, args.high_freq, sr, args.reduce_noise)

if __name__ == '__main__':
    main()
