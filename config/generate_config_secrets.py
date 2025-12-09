import secrets
import yaml
import os

flask_secret = secrets.token_hex(32)
jwt_secret = secrets.token_urlsafe(32)

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print(f"Lỗi: File {config_path} không tồn tại")
    exit(1)
except Exception as e:
    print(f"Lỗi đọc config: {e}")
    exit(1)

if "app" not in config:
    config["app"] = {}

config["app"]["flask_secret_key"] = flask_secret
config["app"]["jwt_secret_key"] = jwt_secret

try:
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("Successfully updated secret keys in config.yaml")
    print(f"   - FLASK_SECRET_KEY: {flask_secret[:40]}...")
    print(f"   - JWT_SECRET_KEY: {jwt_secret[:40]}...")
except Exception as e:
    print(f"Error writing config: {e}")
    exit(1)