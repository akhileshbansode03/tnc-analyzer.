from pypdf import PdfReader
import re


def clean_text(text: str) -> str:
    # Remove extra newlines
    text = re.sub(r'\n+', '\n', text)

    # Join broken lines
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return clean_text(text)