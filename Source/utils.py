import yaml
import numpy as np
import os
import tensorflow as tf
import pickle

CONFIG_PATH = "Source/config/config.yml"


def load_config(config_name):
    with open(config_name) as file:
        config = yaml.safe_load(file)

    return config


def load_dataset_stats(dataset_stats_file):
    """Load dataset statistics from a pickle file."""
    try:
        if tf.io.gfile.exists(dataset_stats_file):
            with tf.io.gfile.GFile(dataset_stats_file, "rb") as f:
                return pickle.load(f)
    except Exception as err:
        print(f"Loading dataset statistics from pickle failed: {err}.")
        return None


def load_audio(audio_folder):
    """Load audio from a numpy file."""
    file_path = os.path.join(audio_folder, "recorded_audio.npy")
    return np.load(file_path, allow_pickle=True)


def save_audio(audio, folder, index):
    """Save audio to a numpy file."""
    path = os.path.join(folder, f"{index}.npy")
    np.save(path, audio)
