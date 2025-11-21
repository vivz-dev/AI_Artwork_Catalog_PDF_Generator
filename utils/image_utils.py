from PIL import Image
import io


def read_uploaded_file(uploaded_file) -> bytes:
    """
    Lee el archivo subido por Streamlit y devuelve su contenido en bytes.
    """
    return uploaded_file.read()


def bytes_to_pil_image(image_bytes: bytes) -> Image.Image:
    """
    Convierte bytes de imagen a un objeto PIL.Image para mostrar en la UI.
    """
    return Image.open(io.BytesIO(image_bytes))
