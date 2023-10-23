import time
import ddsp
import librosa
import numpy as np


class DDSPAudioProcessor:
    @staticmethod
    def compute_features(audio):
        """Compute audio features."""
        start_time = time.time()
        ddsp.spectral_ops.reset_crepe()
        audio_features = ddsp.training.metrics.compute_audio_features(audio)
        audio_features["loudness_db"] = audio_features["loudness_db"].astype(np.float32)
        print(f"Audio features took {time.time() - start_time:.1f} seconds")
        return audio_features

    @staticmethod
    def trim_audio_features(audio_features, time_steps, n_samples):
        """Trim audio features to a given length."""
        for key in ["f0_hz", "f0_confidence", "loudness_db"]:
            audio_features[key] = audio_features[key][:time_steps]
        audio_features["audio"] = audio_features["audio"][:, :n_samples]

    @staticmethod
    def resample_audio(audio, orig_sr, target_sr):
        """Resample audio to target sampling rate."""
        return librosa.resample(audio, orig_sr, target_sr, res_type="kaiser_best")

    @staticmethod
    def resynthesize(model, audio_features):
        """Use model to synthesize audio from features."""
        start_time = time.time()
        outputs = model(audio_features, training=False)
        print(f"Prediction took {time.time() - start_time:.1f} seconds")
        return model.get_audio_from_outputs(outputs).numpy()[0]
