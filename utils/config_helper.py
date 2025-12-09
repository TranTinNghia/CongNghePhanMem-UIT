import yaml
import os
from typing import Optional, Dict

_config_cache = None

def load_config_file() -> Optional[Dict]:
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            _config_cache = yaml.safe_load(f)
        return _config_cache
    except FileNotFoundError:
        print(f"Lỗi: File config/config.yaml không tồn tại tại {config_path}")
        return None
    except Exception as e:
        print(f"Lỗi đọc config.yaml: {e}")
        return None

def get_config(key: str, default=None):
    config = load_config_file()
    if not config:
        return default
    
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value

def get_flask_secret_key() -> str:
    return get_config("app.flask_secret_key", os.urandom(24).hex())

def get_jwt_secret_key() -> str:
    return get_config("app.jwt_secret_key", os.urandom(32).hex())

def get_db_config() -> Optional[Dict]:
    return get_config("database")
