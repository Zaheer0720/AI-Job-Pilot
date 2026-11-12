import os
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF resume using PyMuPDF (fitz) or fallback to pypdf."""
    text = ""
    # Try PyMuPDF first
    try:
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"PyMuPDF parse attempt failed or not installed: {e}")

    # Fallback to pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"pypdf parse failed: {e}")

    if not text.strip():
        raise ValueError("Failed to extract text from PDF file.")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX resume."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {e}")


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text resume."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Failed to read text file: {e}")


def parse_resume_file(file_path: str) -> str:
    """Parse a resume file and return raw text."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use PDF, DOCX, or TXT.")
