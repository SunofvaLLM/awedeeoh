import pyaudio
import argparse

class DeviceManager:
    def __init__(self):
        """
        Initializes the DeviceManager object and prepares the PyAudio instance.
        """
        self.p = pyaudio.PyAudio()
        self.input_device_index = None
        self.output_device_index = None
        self.available_devices = self._list_devices()

    def _list_devices(self):
        """
        Lists all available input and output audio devices.
        
        :return: A list of available devices with their details
        """
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            devices.append({
                'index': i,
                'name': device_info.get('name'),
                'max_input_channels': device_info.get('maxInputChannels'),
                'max_output_channels': device_info.get('maxOutputChannels'),
                'sample_rate': device_info.get('defaultSampleRate')
            })
        return devices

    def list_devices(self):
        """
        Prints the available audio devices (both input and output) to the console.
        """
        print("\nAvailable Audio Devices:")
        for idx, device in enumerate(self.available_devices):
            device_type = "Input" if device['max_input_channels'] > 0 else "Output"
            print(f"{idx + 1}. {device['name']} ({device_type}) - Sample Rate: {device['sample_rate']}Hz")

    def choose_input_device(self):
        """
        Allows the user to select an input device for audio recording.
        """
        while True:
            try:
                device_index = int(input("\nSelect Input Device by number: ")) - 1
                if device_index < 0 or device_index >= len(self.available_devices):
                    print("Invalid choice. Please select a valid device.")
                    continue
                if self.available_devices[device_index]['max_input_channels'] == 0:
                    print("This device doesn't support input. Please choose another one.")
                    continue
                self.input_device_index = device_index
                print(f"Input Device Selected: {self.available_devices[device_index]['name']}")
                break
            except ValueError:
                print("Please enter a valid number.")
    
    def choose_output_device(self):
        """
        Allows the user to select an output device for audio playback.
        """
        while True:
            try:
                device_index = int(input("\nSelect Output Device by number: ")) - 1
                if device_index < 0 or device_index >= len(self.available_devices):
                    print("Invalid choice. Please select a valid device.")
                    continue
                if self.available_devices[device_index]['max_output_channels'] == 0:
                    print("This device doesn't support output. Please choose another one.")
                    continue
                self.output_device_index = device_index
                print(f"Output Device Selected: {self.available_devices[device_index]['name']}")
                break
            except ValueError:
                print("Please enter a valid number.")

    def open_input_device(self):
        """
        Opens the selected input device stream for audio capture.
        
        :return: Input stream object
        """
        if self.input_device_index is None:
            print("No input device selected. Please select one first.")
            return None

        device_info = self.available_devices[self.input_device_index]
        try:
            input_stream = self.p.open(format=pyaudio.paInt16,
                                       channels=1,  # Mono channel for simplicity
                                       rate=int(device_info['sample_rate']),
                                       input=True,
                                       input_device_index=self.input_device_index,
                                       frames_per_buffer=1024)
            print(f"Input stream opened successfully using {device_info['name']}")
            return input_stream
        except IOError as e:
            print(f"Error opening input device: {e}")
            return None

    def open_output_device(self):
        """
        Opens the selected output device stream for audio playback.
        
        :return: Output stream object
        """
        if self.output_device_index is None:
            print("No output device selected. Please select one first.")
            return None

        device_info = self.available_devices[self.output_device_index]
        try:
            output_stream = self.p.open(format=pyaudio.paInt16,
                                        channels=1,  # Mono channel for simplicity
                                        rate=int(device_info['sample_rate']),
                                        output=True,
                                        output_device_index=self.output_device_index,
                                        frames_per_buffer=1024)
            print(f"Output stream opened successfully using {device_info['name']}")
            return output_stream
        except IOError as e:
            print(f"Error opening output device: {e}")
            return None

    def close_streams(self, input_stream, output_stream):
        """
        Properly closes input and output streams.
        
        :param input_stream: Input stream object to close
        :param output_stream: Output stream object to close
        """
        if input_stream:
            input_stream.stop_stream()
            input_stream.close()
            print("Input stream closed.")
        if output_stream:
            output_stream.stop_stream()
            output_stream.close()
            print("Output stream closed.")
        self.p.terminate()

    def terminate(self):
        """
        Terminates the PyAudio instance.
        """
        self.p.terminate()


# CLI interface for device selection
def main():
    parser = argparse.ArgumentParser(description="Manage input/output devices for real-time audio processing.")
    parser.add_argument('--list', action='store_true', help="List available audio devices")
    
    args = parser.parse_args()

    # Initialize device manager
    device_manager = DeviceManager()

    if args.list:
        device_manager.list_devices()
        return

    # Choose input and output devices
    device_manager.list_devices()

    device_manager.choose_input_device()
    device_manager.choose_output_device()

    # Open input and output devices
    input_stream = device_manager.open_input_device()
    output_stream = device_manager.open_output_device()

    # For demo, we will just keep the streams open
    try:
        print("Streams are now open. Press Ctrl+C to exit.")
        while True:
            pass  # Here you could read/write data for processing
    except KeyboardInterrupt:
        print("Closing streams...")
    finally:
        device_manager.close_streams(input_stream, output_stream)
        device_manager.terminate()

if __name__ == '__main__':
    main()
