# /home/ubuntu/ai_content_detector/src/main.py
import sys
import os

# Add project root to Python path - DO NOT CHANGE THIS LINE
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import uuid

# Import utilities
from src.utils.file_processor import process_file, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from src.utils.ocr_processor import perform_ocr
from src.utils.ai_detector import detect_ai_content # Import the AI detector function

# Corrected Flask initialization and config lines
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Corrected route decorator
@app.route('/')
def index():
    """Serves the main HTML page."""
    # Use render_template once index.html is fully ready and tested
    return render_template('index.html')

def analyze_content(text_content):
    """Helper function to run AI detection and handle results/errors."""
    if not text_content or not text_content.strip():
        # Corrected jsonify syntax
        return jsonify({'error': 'No text content found or extracted to analyze.'}), 400

    detection_result, detection_error = detect_ai_content(text_content)

    if detection_error:
        print(f"AI Detection Error: {detection_error}")
        if "Failed to load AI detector model" in detection_error:
             # Corrected jsonify syntax
             return jsonify({'error': 'AI detection model is currently unavailable. Please try again later.'}), 503 # Service Unavailable
        # Corrected jsonify syntax
        return jsonify({'error': f"AI detection failed: {detection_error}"}), 500
    else:
        print(f"AI Detection successful: {detection_result}")
        # Corrected jsonify syntax
        return jsonify({
            'message': 'Content analyzed successfully.',
            'analysis': detection_result,
            # 'original_content': text_content # Optionally return original text, consider size limits
        })

# Corrected route decorator
@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads, processes them (including OCR), and runs AI detection."""
    if 'file' not in request.files:
        # Corrected jsonify syntax
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        # Corrected jsonify syntax
        return jsonify({'error': 'No selected file'}), 400

    ocr_model_type = request.form.get('ocr_model_type', 'printed') # Default to printed

    if file:
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        _, extension = os.path.splitext(filename)
        unique_filename = f"{unique_id}{extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        extracted_text = None

        try:
            file.save(filepath)
            processed_content, file_type_or_error = process_file(filepath)

            if file_type_or_error == "image":
                print(f"Processing image file: {filepath} with OCR model: {ocr_model_type}")
                ocr_text, ocr_error = perform_ocr(filepath, model_type=ocr_model_type)
                if os.path.exists(filepath):
                    os.remove(filepath) # Clean up image file
                if ocr_error:
                    print(f"OCR Error: {ocr_error}")
                    # Corrected jsonify syntax
                    return jsonify({'error': f"OCR failed: {ocr_error}"}), 500
                extracted_text = ocr_text
                print(f"OCR successful, text length: {len(extracted_text)}")

            elif file_type_or_error == "text":
                if os.path.exists(filepath):
                    os.remove(filepath) # Clean up original file
                extracted_text = processed_content
                print(f"Text extracted from file, length: {len(extracted_text)}")

            else: # Handle errors from process_file
                if os.path.exists(filepath):
                    os.remove(filepath)
                print(f"File Processing Error: {file_type_or_error}")
                # Corrected jsonify syntax
                return jsonify({'error': file_type_or_error}), 400

            # Now analyze the extracted text (from file or OCR)
            return analyze_content(extracted_text)

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath) # Ensure cleanup on any exception
            print(f"Error during file upload or processing: {e}")
            # Corrected jsonify syntax
            return jsonify({'error': 'An unexpected error occurred during file processing.'}), 500

    # Corrected jsonify syntax
    return jsonify({'error': 'File upload failed'}), 400

# Corrected route decorator
@app.route('/analyze_text', methods=['POST'])
def analyze_pasted_text():
    """Handles pasted text input for AI detection."""
    data = request.get_json()
    if not data or 'text' not in data:
        # Corrected jsonify syntax
        return jsonify({'error': 'No text provided'}), 400

    text_content = data['text']
    print(f"Received pasted text, length: {len(text_content)}")

    # Analyze the pasted text
    return analyze_content(text_content)


if __name__ == '__main__':
    # IMPORTANT: Host must be 0.0.0.0 to be accessible externally
    # Use a different port if 5000 is common, e.g., 5001
    # Optional: Pre-load models (uncomment if needed, increases startup time)
    # print("Pre-loading models...")
    # from src.utils.ocr_processor import load_ocr_model
    # from src.utils.ai_detector import load_detector_model
    # try:
    #     load_ocr_model("microsoft/trocr-large-printed")
    #     load_ocr_model("microsoft/trocr-large-handwritten")
    #     load_detector_model()
    #     print("Models pre-loaded successfully.")
    # except Exception as preload_error:
    #     print(f"Warning: Model pre-loading failed: {preload_error}")

    app.run(debug=False, host=\'0.0.0.0\', port=5001)
