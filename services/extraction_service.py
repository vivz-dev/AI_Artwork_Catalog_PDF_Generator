# services/extraction_service.py

from typing import Dict

from services.ocr_service import run_ocr


def extract_image_text(image_bytes: bytes, file_name: str) -> Dict[str, object]:
    """
    Ejecuta OCR sobre una imagen y devuelve un dict con:
    - file_name: nombre del archivo
    - ocr_text: texto extraído con Tesseract
    - image_bytes: bytes originales de la imagen (para usar en el PDF)
    """
    ocr_text = run_ocr(image_bytes, lang="eng")  # o "spa", o "eng+spa"
    return {
        "file_name": file_name,
        "ocr_text": ocr_text,
        "image_bytes": image_bytes,
    }
