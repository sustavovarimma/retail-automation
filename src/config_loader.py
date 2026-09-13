"""Загрузка и нормализация конфигурации проекта."""
from pathlib import Path
import yaml


def load_config(path: str = "config/config.yaml") -> dict:
    """Читает YAML-конфиг и преобразует относительные пути в абсолютные."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    root = Path(__file__).resolve().parent.parent
    cfg["paths"]["data_dir"] = root / cfg["paths"]["data_dir"]
    cfg["paths"]["log_dir"] = root / cfg["paths"]["log_dir"]

    cfg["paths"]["data_dir"].mkdir(parents=True, exist_ok=True)
    cfg["paths"]["log_dir"].mkdir(parents=True, exist_ok=True)
    return cfg
