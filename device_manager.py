import pyaudio
import sys

class DeviceManager:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_device_index = None
        self.output_device_index = None

    def list_devices(self):
        """
        Lists all available audio devices and marks inputs and outputs.
        """
        print("\n🎙️ Available Audio Devices:")
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            label = []
            if dev.get('maxInputChannels') > 0:
                label.append("INPUT")
            if dev.get('maxOutputChannels') > 0:
                label.append("OUTPUT")
            print(f"[{i}] {dev['name']} ({', '.join(label)})")

    def choose_input_device(self):
        """
        Prompts user to select an input device index.
        """
        try:
            index = int(input("\n🎧 Enter index of the INPUT device (e.g., your Yeti Mic): "))
            dev = self.p.get_device_info_by_index(index)
            if dev.get('maxInputChannels') < 1:
                raise ValueError("Selected device is not an input device.")
            self.input_device_index = index
            print(f"✅ Selected INPUT device: {dev['name']}")
        except Exception as e:
            print(f"❌ Error selecting input device: {e}")
            sys.exit(1)

    def choose_output_device(self):
        """
        Prompts user to select an output device index.
        """
        try:
            index = int(input("🔊 Enter index of the OUTPUT device (e.g., your Bluetooth headphones): "))
            dev = self.p.get_device_info_by_index(index)
            if dev.get('maxOutputChannels') < 1:
                raise ValueError("Selected device is not an output device.")
            self.output_device_index = index
            print(f"✅ Selected OUTPUT device: {dev['name']}")
        except Exception as e:
            print(f"❌ Error selecting output device: {e}")
            sys.exit(1)

    def open_input_stream(self, rate=44100, frames_per_buffer=1024):
        """
        Opens the selected input stream.
        """
        if self.input_device_index is None:
            raise RuntimeError("Input device not selected.")

        return self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=frames_per_buffer
        )

    def open_output_stream(self, rate=44100, frames_per_buffer=1024):
        """
        Opens the selected output stream.
        """
        if self.output_device_index is None:
            raise RuntimeError("Output device not selected.")

        return self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            output=True,
            output_device_index=self.output_device_index,
            frames_per_buffer=frames_per_buffer
        )

    def terminate(self):
        """
        Properly terminate the PyAudio session.
        """
        self.p.terminate()
