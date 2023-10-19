from utils import load_config


class ConfigManager:
    def __init__(self, config_path):
        self.config = load_config(config_path)

    def get_config(self, key):
        return self.config.get(key, None)
