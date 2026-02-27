import os
import queue
import sounddevice as sd
import numpy as np

class AudioCapture:
    def __init__(self, sample_rate=16000, chunk_duration=2.0):
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        self.audio_queue.put(indata.copy())

    def start_capture(self, device_index=None):
        """
        Starts capturing audio from the specified device.
        On Windows, use WASAPI loopback for system audio if needed.
        """
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                device=device_index
            )
            self.stream.start()
            print("Audio capture started...")
        except Exception as e:
            print(f"Error starting audio capture: {e}")

    def stop_capture(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Audio capture stopped.")

    def get_audio_chunk(self):
        chunks = []
        while not self.audio_queue.empty():
            chunks.append(self.audio_queue.get())
        
        if chunks:
            return np.concatenate(chunks, axis=0)
        return None

def list_audio_devices():
    print(sd.query_devices())
