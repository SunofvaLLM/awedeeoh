import sounddevice as sd

class DeviceManager:
    """
    Manages the detection and listing of audio I/O devices.
    """
    def __init__(self):
        self.devices = sd.query_devices()

    def get_input_devices(self):
        """Returns a dictionary of available input devices."""
        input_devices = {}
        for i, device in enumerate(self.devices):
            # A device is considered an input device if it has > 0 input channels
            if device['max_input_channels'] > 0:
                input_devices[i] = f"{device['name']}"
        return input_devices

    def get_output_devices(self):
        """Returns a dictionary of available output devices."""
        output_devices = {}
        for i, device in enumerate(self.devices):
            # A device is considered an output device if it has > 0 output channels
            if device['max_output_channels'] > 0:
                output_devices[i] = f"{device['name']}"
        return output_devices

    def get_default_input_device_index(self):
        """Gets the index of the default system input device."""
        try:
            return sd.default.device[0]
        except Exception:
            # Fallback if no default is set
            inputs = self.get_input_devices()
            if inputs:
                return list(inputs.keys())[0]
            return None


    def get_default_output_device_index(self):
        """Gets the index of the default system output device."""
        try:
            return sd.default.device[1]
        except Exception:
            # Fallback if no default is set
            outputs = self.get_output_devices()
            if outputs:
                return list(outputs.keys())[0]
            return None

if __name__ == '__main__':
    # Example usage: Print available devices
    manager = DeviceManager()
    
    print("--- Input Devices ---")
    inputs = manager.get_input_devices()
    for index, name in inputs.items():
        print(f"  Index {index}: {name}")
        
    print("\n--- Output Devices ---")
    outputs = manager.get_output_devices()
    for index, name in outputs.items():
        print(f"  Index {index}: {name}")

    print(f"\nDefault Input Index: {manager.get_default_input_device_index()}")
    print(f"Default Output Index: {manager.get_default_output_device_index()}")
