from faster_whisper import WhisperModel
import numpy as np

class Transcriber:
    def __init__(self, model_size="base", device="cpu"):
        # You can use "tiny", "base", "small", "medium", "large-v3"
        # "cpu" or "cuda" (for NVIDIA GPUs)
        print(f"Loading Whisper model ({model_size})...")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, audio_data):
        """
        Transcribes audio data (numpy array).
        """
        if audio_data is None or len(audio_data) == 0:
            return None, None

        # faster-whisper expects float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Reshape if necessary (should be 1D)
        audio_data = audio_data.flatten()

        segments, info = self.model.transcribe(audio_data, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        return full_text.strip(), info.language
