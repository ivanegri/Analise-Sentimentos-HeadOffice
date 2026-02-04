import io
from pypdf import PdfReader
import docx

def parse_pdf(file_stream) -> str:
    """Extracts text from a PDF file stream."""
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_docx(file_stream) -> str:
    """Extracts text from a DOCX file stream."""
    try:
        doc = docx.Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""
