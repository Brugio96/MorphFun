import numpy as np
import librosa
from ddsp.training.postprocessing import detect_notes, fit_quantile_transform
import ddsp


class AudioFeatureModifier:
    """Modifies audio features based on provided configurations and statistics."""

    def __init__(self, audio_features, statistics, config):
        """
        Args:
            audio_features (dict): Dictionary of audio features.
            statistics (dict): Dataset statistics for the audio.
            config (AudioFeatureConfig): Configuration for modifying audio features.
        """
        self.audio_features = {k: v for k, v in audio_features.items()}
        self.statistics = statistics
        self.config = config
        self.mask_on = None
        self.note_on_value = None

    def modify(self):
        """Applies modifications to the audio features based on the configuration.

        Returns:
            dict: Modified audio features.
        """
        if self.config.ADJUST and self.statistics is not None:
            self._apply_auto_adjustment()
        else:
            print(
                "\nSkipping auto-adjust (box not checked or no dataset statistics found)."
            )
        return self.audio_features

    def _apply_auto_adjustment(self):
        """Automatically adjusts audio features based on detected notes."""
        self.mask_on, self.note_on_value = detect_notes(
            self.audio_features["loudness_db"],
            self.audio_features["f0_confidence"],
            self.config.threshold,
        )
        if np.any(self.mask_on):
            self._shift_pitch_register()
            self._quantile_shift_notes()
        else:
            print("\nSkipping auto-adjust (no notes detected or ADJUST box empty).")

    def _shift_pitch_register(self):
        """Shifts the pitch of the audio to match the target mean pitch."""
        target_mean_pitch = self.statistics["mean_pitch"]
        pitch = ddsp.core.hz_to_midi(self.audio_features["f0_hz"])
        mean_pitch = np.mean(pitch[self.mask_on])
        p_diff = target_mean_pitch - mean_pitch
        p_diff_octave = p_diff / 12.0
        round_fn = np.floor if p_diff_octave > 1.5 else np.ceil
        p_diff_octave = round_fn(p_diff_octave)
        self._shift_f0(p_diff_octave)

    def _quantile_shift_notes(self):
        """Shifts the loudness of detected notes using quantile transformation."""
        _, loudness_norm = fit_quantile_transform(
            np.asarray(self.audio_features["loudness_db"]),
            self.mask_on,
            inv_quantile=self.statistics["quantile_transform"],
        )
        mask_off = np.logical_not(self.mask_on)
        loudness_norm[mask_off] -= self.config.quiet * (
            1.0 - self.note_on_value[mask_off][:, np.newaxis]
        )
        loudness_norm = np.reshape(
            loudness_norm, self.audio_features["loudness_db"].shape
        )
        self.audio_features["loudness_db"] = loudness_norm

    def _shift_ld(self, ld_shift=6.0):
        """Shifts the loudness by a specified value.

        Args:
            ld_shift (float): Amount by which to shift the loudness.
        """
        self.audio_features["loudness_db"] += ld_shift

    def _shift_f0(self, pitch_shift=0.0):
        """Shifts the pitch (f0) by a number of octaves.

        Args:
            pitch_shift (float): Number of octaves by which to shift the pitch.
        """
        self.audio_features["f0_hz"] *= 2.0 ** (pitch_shift)
        self.audio_features["f0_hz"] = np.clip(
            self.audio_features["f0_hz"], 0.0, librosa.midi_to_hz(110.0)
        )


class AudioFeatureConfig:
    """Configuration for modifying audio features."""

    def __init__(self):
        self.threshold = 1.0  # Threshold for detecting notes
        self.ADJUST = True  # Flag to determine if adjustments should be applied
        self.quiet = 20  # Value for quieting the audio
        self.autotune = 0.0  # Autotune configuration
        self.pitch_shift = 0  # Number of octaves by which to shift the pitch
        self.loudness_shift = 0  # Value by which to shift the loudness
