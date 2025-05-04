# /home/ubuntu/ai_content_detector/src/utils/file_processor.py

import os
import subprocess
from docx import Document

UPLOAD_FOLDER = '/home/ubuntu/ai_content_detector/uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_txt(filepath):
    """Reads content from a TXT file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error processing TXT file {filepath}: {e}")
        return None

def process_docx(filepath):
    """Extracts text content from a DOCX file."""
    try:
        doc = Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error processing DOCX file {filepath}: {e}")
        return None

def process_pdf(filepath):
    """Extracts text content from a PDF file using pdftotext."""
    try:
        # Use pdftotext to convert PDF to text
        # The output text is written to stdout, so we capture it
        result = subprocess.run(['pdftotext', filepath, '-'], capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout
    except FileNotFoundError:
        print("Error: pdftotext command not found. Make sure poppler-utils is installed.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error processing PDF file {filepath} with pdftotext: {e}")
        # Attempt to read stderr for more details if available
        if e.stderr:
            print(f"pdftotext stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred processing PDF {filepath}: {e}")
        return None

def process_file(filepath):
    """Processes the uploaded file based on its extension."""
    filename = os.path.basename(filepath)
    if not allowed_file(filename):
        return None, "File type not allowed"

    extension = filename.rsplit('.', 1)[1].lower()
    text_content = None
    error_message = None

    if extension == 'txt':
        text_content = process_txt(filepath)
    elif extension == 'docx':
        text_content = process_docx(filepath)
    elif extension == 'pdf':
        text_content = process_pdf(filepath)
    elif extension in {'png', 'jpg', 'jpeg'}:
        # Image processing (OCR) will be handled separately
        # For now, return the path indicating it's an image
        return filepath, "image"
    else:
        error_message = "Unsupported file type"

    if text_content is None and error_message is None:
        error_message = f"Could not extract text from {filename}"

    if error_message:
        return None, error_message
    else:
        return text_content, "text"


