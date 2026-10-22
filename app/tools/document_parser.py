from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def parse_document(file_path: str | Path) -> str:
    """
    Extracts text content from PDF, images, or TXT files.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found at: {file_path}")

    suffix = path.suffix.lower()

    if suffix in [".txt", ".log", ".json"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif suffix == ".pdf":
        extracted_text = []
        with fitz.open(path) as doc:
            for page in doc:
                text = page.get_text()
                extracted_text.append(text)
        return "\n".join(extracted_text)

    elif suffix in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        try:
            image = Image.open(path)
            return pytesseract.image_to_string(image)
        except Exception:
            return "[OCR text extraction unavailable or empty for image]"

    else:
        # Fallback reading
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"[Error parsing document: {str(e)}]"