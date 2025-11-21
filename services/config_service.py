# services/config_service.py

import json
import os
from typing import Dict, Any

CONFIG_DIR = "config"
CONFIG_PATH = os.path.join(CONFIG_DIR, "user_settings.json")


def load_user_settings() -> Dict[str, Any]:
    """
    Carga la configuración del usuario desde un JSON.
    Si no existe, devuelve un dict vacío.
    """
    if not os.path.isfile(CONFIG_PATH):
        return {}

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except Exception as e:
        print(f"[WARN] No se pudo cargar la configuración: {e}")
        return {}


def save_user_settings(settings: Dict[str, Any]) -> None:
    """
    Guarda la configuración del usuario en un JSON.
    Crea la carpeta config/ si no existe.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] No se pudo guardar la configuración: {e}")
