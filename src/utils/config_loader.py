import yaml
import os


def load_config():
    """
    Tự động tìm và load file config.yml từ thư mục gốc của project.
    """
    # Tìm đường dẫn tuyệt đối đến thư mục gốc của project
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    config_path = os.path.join(root_dir, 'config.yml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Không tìm thấy file config tại: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Biến global để dùng nhanh
cfg = load_config()