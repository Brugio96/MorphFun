import os
import ddsp
import time
import tensorflow as tf

MODEL_DIR = "Source/models"


class ModelManager:
    def __init__(self, config):
        self.model_names = config["morphing"]["model_names"]
        self.model_files = self._retrieve_model_paths()
        self.models = {}

    def _retrieve_model_paths(self):
        """Retrieve paths for model related files."""
        paths = {}
        for model_name in self.model_names:
            model_dir_path = os.path.join(os.getcwd(), f"{MODEL_DIR}/{model_name}")
            paths[model_name] = {
                **self._model_files_from_directory(model_dir_path),
                "model_dir": model_dir_path,
            }
        return paths

    def _model_files_from_directory(self, model_dir):
        """Retrieve paths for checkpoint, dataset stats, and gin config."""
        ckpt_files = [f for f in tf.io.gfile.listdir(model_dir) if "ckpt" in f]
        ckpt_name = ckpt_files[0].split(".")[0]
        ckpt = os.path.join(model_dir, ckpt_name)
        return {
            "dataset_stats_file": os.path.join(model_dir, "dataset_statistics.pkl"),
            "gin_file": os.path.join(model_dir, "operative_config-0.gin"),
            "ckpt": ckpt,
        }

    def load_model(self, path, audio_features):
        """Load and return the model for a given path."""
        start_time = time.time()
        model = ddsp.training.models.Autoencoder()
        model.restore(path["ckpt"])
        _ = model(audio_features, training=False)
        print(f"Restoring model took {time.time() - start_time:.1f} seconds")
        return model

    def get_model_files(self, index):
        """Get model files for a given index."""
        return self.model_files[self.model_names[index]]
