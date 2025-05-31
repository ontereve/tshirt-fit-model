# utils/config_loader.py

import yaml
import os

def load_model_config(path="config/model_config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)
