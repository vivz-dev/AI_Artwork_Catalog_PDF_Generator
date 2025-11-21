# app.py

import concurrent.futures
import os

import streamlit as st
from PIL import Image

from utils.image_utils import read_uploaded_file, bytes_to_pil_image
from services.extraction_service import extract_image_text
from services.pdf_service import build_ocr_pdf
from services.config_service import load_user_settings, save_user_settings
from ui_styles import MAIN_CSS


# ==== DEFAULT LOGO PATH ====
DEFAULT_LOGO_PATH = "assets/knb+art+advisory-3.webp"


# ==== HELPERS ====

def hex_to_rgb(hex_color: str):
    """Convert '#RRGGBB' to (r, g, b)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def get_page_size_mm(page_format: str):
    """
    Returns (width_mm, height_mm) for A4 or Letter in portrait.
    If orientation is landscape, values will be swapped later.
    """
    page_format = page_format.lower()
    if page_format == "letter":
        # 8.5 x 11 inches approx.
        return 216, 279
    # Default A4: 210 x 297 mm
    return 210, 297


def compute_logo_position(position_key: str, page_format: str, orientation: str, logo_width_mm: float):
    """
    Computes (x, y) for logo based on:
    - position_key: 'top-left', 'top-center', 'top-right',
                    'bottom-left', 'bottom-center', 'bottom-right'
    - page_format: 'A4' or 'letter'
    - orientation: 'P' or 'L'
    - logo_width_mm: logo width in mm
    """
    page_w, page_h = get_page_size_mm(page_format)
    if orientation == "L":  # landscape
        page_w, page_h = page_h, page_w

    margin = 10  # margin from borders

    # Y axis
    if position_key.startswith("top"):
        y = margin
    else:  # bottom
        y = page_h - logo_width_mm - margin

    # X axis
    if position_key.endswith("left"):
        x = margin
    elif position_key.endswith("right"):
        x = page_w - logo_width_mm - margin
    else:  # center
        x = (page_w - logo_width_mm) / 2.0

    return x, y


def prepare_logo_image(
    use_default: bool,
    uploaded_logo_file,
    stored_logo_path: str,
) -> tuple[Image.Image | None, str]:
    """
    Returns (logo_pil_image, label) to display in the UI.

    - If use_default=True, tries DEFAULT_LOGO_PATH.
    - If use_default=False, uses the uploaded logo (this session),
      or the stored_logo_path (previously saved custom logo).
    """
    logo_pil_image = None
    label = ""

    if use_default:
        path = DEFAULT_LOGO_PATH
        if os.path.isfile(path):
            try:
                logo_pil_image = Image.open(path)
                label = "Default logo"
            except Exception as e:
                print(f"[WARN] Could not open default logo: {e}")
                label = "Error opening default logo"
        else:
            label = "Default logo not found"
    else:
        # Logo uploaded in this session
        if uploaded_logo_file is not None:
            try:
                logo_pil_image = Image.open(uploaded_logo_file)
                label = "Custom logo (current session)"
            except Exception as e:
                print(f"[WARN] Could not open uploaded logo: {e}")
                label = "Error opening uploaded logo"
        # Custom logo saved previously
        elif stored_logo_path and os.path.isfile(stored_logo_path):
            try:
                logo_pil_image = Image.open(stored_logo_path)
                label = "Custom logo (saved)"
            except Exception as e:
                print(f"[WARN] Could not open saved logo: {e}")
                label = "Error opening saved logo"
        else:
            label = "No custom logo"

    return logo_pil_image, label


def save_logo_persistent(logo_pil_image: Image.Image) -> str:
    """
    Saves the custom logo under assets/ so it persists across sessions.
    """
    os.makedirs("assets", exist_ok=True)
    path = os.path.join("assets", "custom_logo_saved.png")
    logo_pil_image.save(path, format="PNG")
    return path


def save_logo_temp(logo_pil_image: Image.Image) -> str:
    """
    Saves the logo as a temporary PNG (for FPDF) and returns the path.
    """
    temp_path = "temp_logo_runtime.png"
    logo_pil_image.save(temp_path, format="PNG")
    return temp_path


# ==== LOAD PERSISTENT SETTINGS ====
stored_settings = load_user_settings()

stored_logo_mode = stored_settings.get("logo_mode", "default")  # "default" or "custom"
stored_logo_path = stored_settings.get("logo_path", DEFAULT_LOGO_PATH)

stored_logo_width_mm = stored_settings.get("logo_width_mm", 25)
stored_logo_position_key = stored_settings.get("logo_position_key", "top-left")

stored_page_format = stored_settings.get("page_format", "A4")       # "A4" or "letter"
stored_orientation = stored_settings.get("orientation", "P")        # "P" or "L"

stored_title_font_family = stored_settings.get("title_font_family", "Arial")
stored_title_font_size = float(stored_settings.get("title_font_size", 14.0))

stored_body_font_family = stored_settings.get("body_font_family", "Arial")
stored_body_font_size = float(stored_settings.get("body_font_size", 11.0))

stored_title_color_hex = stored_settings.get("title_color_hex", "#1E40AF")
stored_body_color_hex = stored_settings.get("body_color_hex", "#0F172A")


# ==== STREAMLIT BASIC CONFIG ====
st.set_page_config(
    page_title="AI Artwork Catalog Generator",
    page_icon="🎨",
    layout="wide",
)

# --- GLOBAL CSS ---
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# --- MAIN TITLE ---
st.markdown(
    """
    <div class="main-block">
        <h1>🎨 AI Artwork Catalog Generator (Demo)</h1>
        <p>
            Upload artwork images that include the painting and its text.
            We will extract the text with OCR and generate a PDF containing your logo,
            the artwork image, and the extracted text.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
#   SIDEBAR: CONFIGURATION
# =========================
with st.sidebar:
    st.header("⚙️ PDF & Logo Settings")

    # --- LOGO ---
    st.subheader("Logo")

    logo_options = ["Use default logo", "Use custom logo"]
    default_logo_index = 0 if stored_logo_mode == "default" else 1

    logo_source = st.radio(
        "Which logo do you want to use?",
        logo_options,
        index=default_logo_index,
    )
    use_default_logo = logo_source == "Use default logo"

    uploaded_logo_file = None
    if not use_default_logo:
        uploaded_logo_file = st.file_uploader(
            "Upload logo (png, jpg, jpeg, webp)",
            type=["png", "jpg", "jpeg", "webp"],
            key="logo_uploader",
        )

    # Preview logo
    logo_pil_image, logo_label = prepare_logo_image(
        use_default=use_default_logo,
        uploaded_logo_file=uploaded_logo_file,
        stored_logo_path=stored_logo_path,
    )

    if logo_pil_image is not None:
        st.image(logo_pil_image, caption=logo_label, use_container_width=True)
    else:
        st.caption(logo_label or "No logo selected")

    # Logo width
    logo_width_mm = st.slider(
        "Logo width (mm)",
        min_value=10,
        max_value=80,
        value=int(stored_logo_width_mm),
        step=1,
    )

    # Logo position
    st_pos_options = [
        "Top left",
        "Top center",
        "Top right",
        "Bottom left",
        "Bottom center",
        "Bottom right",
    ]
    pos_key_map = {
        "Top left": "top-left",
        "Top center": "top-center",
        "Top right": "top-right",
        "Bottom left": "bottom-left",
        "Bottom center": "bottom-center",
        "Bottom right": "bottom-right",
    }
    reverse_pos_map = {v: k for k, v in pos_key_map.items()}
    stored_pos_label = reverse_pos_map.get(stored_logo_position_key, "Top left")
    default_pos_index = st_pos_options.index(stored_pos_label)

    pos_option = st.selectbox(
        "Logo position",
        st_pos_options,
        index=default_pos_index,
    )
    logo_position_key = pos_key_map[pos_option]

    # --- PAGE FORMAT ---
    st.subheader("Page format")

    page_size_label = st.selectbox(
        "Page size",
        ["A4", "US Letter"],
        index=0 if stored_page_format.upper() == "A4" else 1,
    )
    pdf_page_format = "A4" if page_size_label == "A4" else "letter"

    orient_label = st.selectbox(
        "Orientation",
        ["Portrait", "Landscape"],
        index=0 if stored_orientation == "P" else 1,
    )
    pdf_orientation = "P" if orient_label == "Portrait" else "L"

    # --- TYPOGRAPHY ---
    st.subheader("Typography")

    font_options = ["Arial", "Times", "Courier"]

    def font_index(value: str) -> int:
        return font_options.index(value) if value in font_options else 0

    title_font_family = st.selectbox(
        "Title font family",
        font_options,
        index=font_index(stored_title_font_family),
    )
    title_font_size = st.number_input(
        "Title font size",
        min_value=8.0,
        max_value=36.0,
        value=float(stored_title_font_size),
        step=1.0,
    )

    body_font_family = st.selectbox(
        "Body font family",
        font_options,
        index=font_index(stored_body_font_family),
    )
    body_font_size = st.number_input(
        "Body font size",
        min_value=8.0,
        max_value=36.0,
        value=float(stored_body_font_size),
        step=1.0,
    )

    # --- COLORS ---
    st.subheader("Text colors")

    title_color_hex = st.color_picker(
        "Title color",
        value=stored_title_color_hex,
    )
    body_color_hex = st.color_picker(
        "Body text color",
        value=stored_body_color_hex,
    )

    title_color_rgb = hex_to_rgb(title_color_hex)
    body_color_rgb = hex_to_rgb(body_color_hex)

    # --- SAVE SETTINGS BUTTON ---
    st.markdown("---")
    if st.button("💾 Save current settings as default"):
        # Logo mode
        new_logo_mode = "default" if use_default_logo else "custom"

        # Persist custom logo if needed
        new_logo_path = DEFAULT_LOGO_PATH
        if new_logo_mode == "default":
            new_logo_path = DEFAULT_LOGO_PATH
        else:
            if logo_pil_image is not None:
                new_logo_path = save_logo_persistent(logo_pil_image)
            else:
                new_logo_path = stored_logo_path if stored_logo_path else DEFAULT_LOGO_PATH

        new_settings = {
            "logo_mode": new_logo_mode,
            "logo_path": new_logo_path,
            "logo_width_mm": logo_width_mm,
            "logo_position_key": logo_position_key,
            "page_format": pdf_page_format,
            "orientation": pdf_orientation,
            "title_font_family": title_font_family,
            "title_font_size": float(title_font_size),
            "body_font_family": body_font_family,
            "body_font_size": float(body_font_size),
            "title_color_hex": title_color_hex,
            "body_color_hex": body_color_hex,
        }

        save_user_settings(new_settings)
        st.success("Settings saved. They will be used automatically next time you open the app.")

# =========================
#   MAIN: IMAGE UPLOAD
# =========================

st.write("")

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    uploaded_files = st.file_uploader(
        "Drag and drop artwork images here (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

images_data = []

if uploaded_files:
    # Convert UploadedFile to bytes + name
    for uploaded in uploaded_files:
        file_bytes = read_uploaded_file(uploaded)
        images_data.append(
            {
                "name": uploaded.name,
                "bytes": file_bytes,
            }
        )

    # --- IMAGE PREVIEW ---
    st.markdown("### Preview")
    cols = st.columns(3)

    for idx, img_info in enumerate(images_data):
        col = cols[idx % 3]
        with col:
            try:
                pil_img = bytes_to_pil_image(img_info["bytes"])
                col.image(
                    pil_img,
                    caption=img_info["name"],
                    use_container_width=True,
                )
            except Exception:
                col.warning(f"Could not display image: {img_info['name']}")

    st.write("")

    # --- PROCESS & GENERATE PDF ---
    st.markdown("---")
    st.markdown("### OCR and PDF generation")

    process_button = st.button(
        "Generate PDF with OCR text and current settings",
        type="primary",
    )

    if process_button:
        st.info("Running OCR on all images in parallel...")

        with st.spinner("Extracting text and building the PDF..."):
            # 1) OCR in parallel
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(8, len(images_data))
            ) as executor:
                futures = [
                    executor.submit(
                        extract_image_text,
                        img_info["bytes"],
                        img_info["name"],
                    )
                    for img_info in images_data
                ]

                ocr_results = []
                for future in concurrent.futures.as_completed(futures):
                    ocr_results.append(future.result())

            # 2) Prepare logo for PDF, if any
            logo_for_pdf_path = None
            if logo_pil_image is not None:
                logo_for_pdf_path = save_logo_temp(logo_pil_image)

            # 3) Compute logo position (x, y)
            logo_x, logo_y = compute_logo_position(
                position_key=logo_position_key,
                page_format=pdf_page_format,
                orientation=pdf_orientation,
                logo_width_mm=logo_width_mm,
            )

            # 4) Build PDF
            pdf_bytes = build_ocr_pdf(
                ocr_items=ocr_results,
                logo_path=logo_for_pdf_path,
                logo_x=logo_x,
                logo_y=logo_y,
                logo_width=logo_width_mm,
                page_format=pdf_page_format,
                orientation=pdf_orientation,
                title_font_family=title_font_family,
                title_font_size=title_font_size,
                body_font_family=body_font_family,
                body_font_size=body_font_size,
                title_color=title_color_rgb,
                body_color=body_color_rgb,
            )

        st.success("PDF generated successfully!")

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name="artwork_catalog_demo.pdf",
            mime="application/pdf",
        )
else:
    st.info("Upload at least one artwork image to get started.")
