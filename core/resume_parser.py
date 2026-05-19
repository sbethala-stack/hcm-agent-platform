import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = _try_pdfplumber(file_bytes)
    if text and len(text.strip()) > 100:
        return text.strip()
    return _try_fitz(file_bytes).strip()


def _try_pdfplumber(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
    except Exception:
        return ""


def _try_fitz(file_bytes: bytes) -> str:
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        return "\n".join(pages)
    except Exception:
        return ""