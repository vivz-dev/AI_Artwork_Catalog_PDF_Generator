# ui_styles.py

MAIN_CSS = """
<style>
.main-block {
    padding: 0;
    text-align: center;
}

/* Contenedor general del uploader */
.stFileUploader {
    margin-top: 1rem;
}

/* Cuadro real de drag & drop (estado base) */
.stFileUploader div[data-testid="stFileDropzone"] {
    border: 2px dashed #38bdf8;   /* borde celeste como en tu ejemplo */
    border-radius: 10px;
    padding: 40px 20px;
    background-color: #0f172a;    /* fondo oscuro */
    transition:
        border-color 0.2s ease,
        background-color 0.2s ease,
        box-shadow 0.2s ease;
}

/* Estado hover (cuando pasas el mouse por encima del cuadro) */
.stFileUploader div[data-testid="stFileDropzone"]:hover {
    border-color: #0ea5e9;
    background-color: #1d4ed8;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.4);
}

/* Texto interno del uploader */
.stFileUploader div[data-testid="stFileDropzone"] span {
    font-size: 0.95rem;
}
</style>
"""
