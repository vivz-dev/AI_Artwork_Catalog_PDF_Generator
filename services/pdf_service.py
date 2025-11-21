# services/pdf_service.py

from typing import List, Dict, Optional, Tuple

import os
import io
from fpdf import FPDF
from PIL import Image


def _to_latin1(text) -> str:
    """
    FPDF uses latin-1 internally, so we convert text to avoid encoding errors.
    Accepts any object and converts it to str.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    return text.encode("latin-1", "replace").decode("latin-1")


def _normalize_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Normalizes a color tuple (r, g, b) into integers in range 0–255.
    """
    if not isinstance(color, (tuple, list)) or len(color) != 3:
        return (0, 0, 0)
    r, g, b = color
    return int(r), int(g), int(b)


def build_ocr_pdf(
    ocr_items: List[Dict[str, object]],
    # Logo
    logo_path: Optional[str] = None,
    logo_x: float = 10,
    logo_y: float = 8,
    logo_width: float = 25,
    # Page format
    page_format: str = "A4",          # "A4" or "letter"
    orientation: str = "P",           # "P" (portrait) or "L" (landscape)
    # Typography & colors
    title_font_family: str = "Arial", # kept for compatibility
    title_font_size: float = 14,
    body_font_family: str = "Arial",
    body_font_size: float = 11,
    title_color: Tuple[int, int, int] = (15, 23, 42),
    body_color: Tuple[int, int, int] = (15, 23, 42),
) -> bytes:
    """
    Builds a PDF from a list of OCR results, placing logo, centered artwork image and centered text.

    Each element of ocr_items must contain at least:
        {
            "file_name": "artwork_file.jpg",
            "ocr_text": "extracted text...",
            "image_bytes": original_image_bytes
        }

    NOTE: The file name is NOT printed anymore; only the demo notice,
    the artwork image and the OCR text are included.
    """
    # Normalize colors
    title_r, title_g, title_b = _normalize_color(title_color)
    body_r, body_g, body_b = _normalize_color(body_color)

    pdf = FPDF(orientation=orientation, unit="mm", format=page_format)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Is logo available?
    use_logo = logo_path is not None and os.path.isfile(logo_path)

    # Sort by file name for consistency (even if we do not print it)
    ocr_items_sorted = sorted(ocr_items, key=lambda x: str(x.get("file_name", "")))

    # Temp directory for artwork images
    os.makedirs("tmp_images", exist_ok=True)

    for idx, item in enumerate(ocr_items_sorted):
        file_name = str(item.get("file_name", "unknown"))
        ocr_text = str(item.get("ocr_text", ""))
        image_bytes = item.get("image_bytes", None)

        pdf.add_page()

        # ---- LOGO (if any) ----
        if use_logo:
            try:
                pdf.image(logo_path, x=logo_x, y=logo_y, w=logo_width)
            except Exception as e:
                print(f"[WARN] Could not draw logo: {e}")

        # Small top margin below the logo
        if use_logo:
            top_margin = logo_y + logo_width + 2  # tighter spacing
        else:
            top_margin = 20

        # Width inside margins
        text_width = pdf.w - pdf.l_margin - pdf.r_margin

        # ==== DEMO NOTICE (centered, no big gap) ====
        pdf.set_xy(pdf.l_margin, top_margin)
        pdf.set_font(body_font_family, "", body_font_size)
        pdf.set_text_color(200, 0, 0)  # red
        demo_text = "This is a demo. Please contact the developer for full access."
        pdf.multi_cell(text_width, 6, _to_latin1(demo_text), align="C")
        pdf.ln(2)  # small gap

        # Current Y after the demo line
        current_y = pdf.get_y()

        # ---- ARTWORK IMAGE (centered horizontally) ----
        text_start_y = current_y  # default if no image

        if image_bytes:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img_w_px, img_h_px = img.size if img.size != (0, 0) else (1, 1)

                # Available page width (mm) inside margins
                page_width_mm = text_width

                # Desired image width: use up to 80% of available width, capped
                artwork_w_mm = min(120.0, page_width_mm * 0.8)
                # Proportional height (mm)
                artwork_h_mm = artwork_w_mm * img_h_px / img_w_px

                # Save temp PNG so FPDF can read it
                art_path = os.path.join("tmp_images", f"art_{idx}.png")
                img.save(art_path, format="PNG")

                # Center horizontally
                image_x = (pdf.w - artwork_w_mm) / 2.0
                image_y = current_y
                pdf.image(art_path, x=image_x, y=image_y, w=artwork_w_mm)

                text_start_y = image_y + artwork_h_mm + 4

            except Exception as e:
                print(f"[WARN] Could not draw artwork image {file_name}: {e}")
                text_start_y = current_y

        # ---- OCR TEXT (centered, below image or demo notice) ----
        pdf.set_xy(pdf.l_margin, text_start_y)
        pdf.set_font(body_font_family, "", body_font_size)
        pdf.set_text_color(body_r, body_g, body_b)
        pdf.multi_cell(
            text_width,
            6,
            _to_latin1(ocr_text if ocr_text else "[No text detected]"),
            align="C",  # center each line
        )

    # Return PDF as bytes (handles different fpdf2 versions)
    raw = pdf.output(dest="S")
    if isinstance(raw, (bytes, bytearray)):
        pdf_bytes = bytes(raw)
    else:
        pdf_bytes = str(raw).encode("latin-1", "replace")

    return pdf_bytes
