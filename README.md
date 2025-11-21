# AI Artwork Catalog PDF Generator

A Streamlit application that turns artwork images into a clean, branded PDF catalog.

Users upload images that contain both the artwork and accompanying text (e.g., exhibition posters or artwork cards). The generates a multi-page PDF including:

- A gallery/brand logo
- The original artwork image
- The extracted text under the image

All layout, typography and branding options are configurable from the UI and persisted across sessions.

---

## Features

- 🖼 **Artwork upload**
  - Drag-and-drop support for multiple images (`JPG`, `JPEG`, `PNG`)
  - Inline thumbnail preview grid

- 🔍 **OCR pipeline with Tesseract**
  - Parallel processing of images to keep the UI responsive

- 📄 **PDF catalog generation**
  - Per-image page containing:
    - Brand logo
    - Centered artwork image
    - Centered extracted text
  - Supports A4 and US Letter, portrait or landscape

- 🎨 **Fully configurable layout & branding (from the UI)**
  - Logo:
    - Default logo from `assets/knb+art+advisory-3.webp`
    - Or user-uploaded custom logo
    - Adjustable width (mm)
    - 6 predefined positions:
      - Top / Bottom × Left / Center / Right
  - Typography:
    - Separate font family for titles and body (`Arial`, `Times`, `Courier`)
    - Custom font sizes for titles and body text
    - Independent color pickers (title and body)
  - Page format:
    - A4 or US Letter
    - Portrait or Landscape

- 💾 **Persistent settings**
  - All UI settings (logo choice, page format, colors, fonts, etc.) are saved to `config/user_settings.json`
  - Custom logo is stored under `assets/custom_logo_saved.png`
  - Settings are automatically reloaded on every app start (even after refreshing or closing the browser)

---

## Tech Stack

- **Frontend / App**: [Streamlit](https://streamlit.io/)
- **OCR**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) via `pytesseract`
- **Image handling**: `Pillow`
- **PDF generation**: `fpdf2`
- **Data / utils**: `numpy`, custom helper modules

---

## Try it!
[Demo Online](https://ai-artwork-catalog-generator.streamlit.app/)

