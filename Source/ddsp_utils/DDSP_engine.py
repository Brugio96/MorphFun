import time
import warnings
import gin

from ddsp_utils.DDSP_audio_processor import DDSPAudioProcessor
from ddsp_utils.DDSP_model_manager import ModelManager
from utils import load_config, CONFIG_PATH, load_dataset_stats, load_audio, save_audio
from ddsp_utils.DDSP_features import AudioFeatureConfig, AudioFeatureModifier

# Constants
SR = 16000
TARGET_SR = 44100
WARNINGS_FILTER = "ignore"
warnings.filterwarnings(WARNINGS_FILTER)


class DDSPConfigManager:
    """Manages the configuration for DDSP models."""

    def __init__(self):
        """Initializes the configuration manager."""
        self._unlock_config()

    def _unlock_config(self):
        """Unlocks the gin configuration, allowing changes."""
        with gin.unlock_config():
            pass

    def configure_model_params(self, model_files):
        """Configures the model parameters using a provided gin file.

        Args:
            model_files (dict): Dictionary containing paths to model files, including the gin file.
        """
        gin.parse_config_file(model_files["gin_file"], skip_unknown=True)

    def configure_audio_params(self, audio):
        """Configures audio parameters based on the provided audio and gin settings.

        Args:
            audio (ndarray): Input audio data.

        Returns:
            tuple: time_steps and n_samples values derived from the audio.
        """
        # Get parameters from gin configuration
        time_steps_train = gin.query_parameter("F0LoudnessPreprocessor.time_steps")
        n_samples_train = gin.query_parameter("Harmonic.n_samples")
        hop_size = int(n_samples_train / time_steps_train)
        time_steps = int(audio.shape[1] / hop_size)
        n_samples = time_steps * hop_size

        # Set new values for some parameters based on the audio data
        gin_params = [
            f"Harmonic.n_samples = {n_samples}",
            f"FilteredNoise.n_samples = {n_samples}",
            f"F0LoudnessPreprocessor.time_steps = {time_steps}",
            "oscillator_bank.use_angular_cumsum = True",
        ]
        gin.parse_config(gin_params)

        return time_steps, n_samples


class DDSPAudioManager:
    """Manages audio operations including loading, processing, and resynthesis."""

    def __init__(self, config):
        """Initializes the DDSPAudioManager with a given configuration.

        Args:
            config (dict): Configuration parameters.
        """
        self._config = config

    def load_audio(self, audio_folder):
        """Loads audio from a specified folder.

        Args:
            audio_folder (str): Path to the audio folder.

        Returns:
            ndarray: Loaded audio data.
        """
        return load_audio(audio_folder)

    def configure_audio_features(self, audio, model_files):
        """Configures audio features based on the provided audio and model files.

        Args:
            audio (ndarray): Input audio data.
            model_files (dict): Dictionary containing paths to model files.

        Returns:
            dict: Dictionary of audio features.
        """
        audio_features = DDSPAudioProcessor.compute_features(audio)
        dataset_stats = load_dataset_stats(model_files["dataset_stats_file"])
        config_manager = DDSPConfigManager()
        config_manager.configure_model_params(model_files)
        time_steps, n_samples = config_manager.configure_audio_params(audio)
        DDSPAudioProcessor.trim_audio_features(audio_features, time_steps, n_samples)

        # Modify audio features using the AudioFeatureModifier class
        modifier_config = AudioFeatureConfig()
        modifier = AudioFeatureModifier(audio_features, dataset_stats, modifier_config)
        modified_features = modifier.modify()

        return modified_features or audio_features

    def resynthesize(self, model, audio_features):
        """Resynthesizes audio using a provided model and audio features.

        Args:
            model (Model): DDSP model.
            audio_features (dict): Dictionary of audio features.

        Returns:
            ndarray: Resynthesized audio data.
        """
        return DDSPAudioProcessor.resynthesize(model, audio_features)

    def resample_audio(self, audio, source_sr, target_sr):
        """Resamples audio from a source sample rate to a target sample rate.

        Args:
            audio (ndarray): Input audio data.
            source_sr (int): Source sample rate.
            target_sr (int): Target sample rate.

        Returns:
            ndarray: Resampled audio data.
        """
        return DDSPAudioProcessor.resample_audio(audio, source_sr, target_sr)


class DDSPEngine:
    """Main engine to manage and transform audio using DDSP models."""

    def __init__(self, config_path=CONFIG_PATH):
        """Initializes the DDSPEngine with a configuration path.

        Args:
            config_path (str): Path to the configuration file.
        """
        self._config = load_config(config_path)
        self._model_manager = ModelManager(self._config)
        self._audio_manager = DDSPAudioManager(self._config)

    def transform_audio(self):
        """Transforms audio based on the configuration and models."""
        audio_folder = self._config["files"]["audio"]
        audio = self._audio_manager.load_audio(audio_folder)
        audio = self._audio_manager.resample_audio(
            audio.ravel(), TARGET_SR, SR
        ).reshape((1, -1))
        audio_features = self._audio_manager.configure_audio_features(
            audio, self._model_manager.get_model_files(0)
        )

        for index, name in enumerate(self._model_manager.model_names):
            processed_audio = self._process_with_model(index, name, audio_features)
            save_audio(processed_audio, audio_folder, index)

    def _process_with_model(self, index, name, audio_features):
        """Processes audio using a specific model.

        Args:
            index (int): Index of the model.
            name (str): Name of the model.
            audio_features (dict): Dictionary of audio features.

        Returns:
            ndarray: Processed audio data.
        """
        start_process_time = time.time()
        model_files = self._model_manager.get_model_files(index)
        model = self._get_or_load_model(name, model_files, audio_features)
        new_audio = self._audio_manager.resynthesize(model, audio_features)
        new_audio = self._audio_manager.resample_audio(new_audio, SR, TARGET_SR)
        print(f"Total time: {time.time() - start_process_time:.1f} seconds")
        return new_audio

    def _get_or_load_model(self, name, model_files, audio_features):
        """Gets a model if already loaded or loads it if not.

        Args:
            name (str): Name of the model.
            model_files (dict): Dictionary containing paths to model files.
            audio_features (dict): Dictionary of audio features.

        Returns:
            Model: Loaded DDSP model.
        """
        if name not in self._model_manager.models:
            self._model_manager.models[name] = self._model_manager.load_model(
                model_files, audio_features
            )
        return self._model_manager.models[name]
