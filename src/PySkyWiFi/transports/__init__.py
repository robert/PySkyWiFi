import os

import yaml

CONFIG_PATH = os.path.expanduser("~/.PySkyWiFi")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)
