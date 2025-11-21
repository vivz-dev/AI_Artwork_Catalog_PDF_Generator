# services/ocr_service.py

import io
from typing import Optional

from PIL import Image
import pytesseract


def run_ocr(image_bytes: bytes, lang: Optional[str] = "eng") -> str:
    """
    Aplica OCR con Tesseract a una imagen en bytes y devuelve el texto detectado.

    Parameters
    ----------
    image_bytes : bytes
        Contenido de la imagen (jpg, png, etc.) en bytes.
    lang : str, opcional
        Idioma(s) para Tesseract. Ejemplos:
        - "eng"      -> inglés
        - "spa"      -> español
        - "eng+spa"  -> inglés + español

    Returns
    -------
    str
        Texto extraído de la imagen.
    """
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang=lang)
    return text.strip()
