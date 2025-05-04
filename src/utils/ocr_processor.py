# /home/ubuntu/ai_content_detector/src/utils/ocr_processor.py

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import os

# Dictionary to cache loaded models and processors to avoid reloading
models_cache = {}

def load_ocr_model(model_name):
    """Loads the specified TrOCR model and processor, caching them."""
    if model_name in models_cache:
        return models_cache[model_name]

    print(f"Loading OCR model: {model_name}...")
    try:
        processor = TrOCRProcessor.from_pretrained(model_name)
        model = VisionEncoderDecoderModel.from_pretrained(model_name)
        # Check if CUDA is available and move model to GPU if possible
        if torch.cuda.is_available():
            print("CUDA available, moving model to GPU.")
            model.to("cuda")
        else:
            print("CUDA not available, using CPU.")
        models_cache[model_name] = (processor, model)
        print(f"Model {model_name} loaded successfully.")
        return processor, model
    except Exception as e:
        print(f"Error loading OCR model {model_name}: {e}")
        return None, None

# Corrected default value quotes
def perform_ocr(image_path, model_type="printed"):
    """Performs OCR on the given image using the specified model type."""
    if not os.path.exists(image_path):
        return None, f"Image file not found: {image_path}"

    # Corrected model name quotes
    if model_type == "printed":
        model_name = "microsoft/trocr-large-printed"
    elif model_type == "handwritten":
        model_name = "microsoft/trocr-large-handwritten"
    else:
        # Corrected error message quotes
        return None, "Invalid model type specified. Choose \"printed\" or \"handwritten\"."

    processor, model = load_ocr_model(model_name)
    if not processor or not model:
        return None, f"Failed to load OCR model: {model_name}"

    try:
        # Corrected convert method quotes
        image = Image.open(image_path).convert("RGB")
        print(f"Processing image: {image_path} with {model_name}")

        # Prepare image for model
        # Corrected return_tensors value quotes
        pixel_values = processor(images=image, return_tensors="pt").pixel_values

        # Move pixel values to GPU if model is on GPU
        if torch.cuda.is_available():
            # Corrected device name quotes
            pixel_values = pixel_values.to("cuda")

        # Generate text IDs
        # Adjust max_length as needed, default is often sufficient
        generated_ids = model.generate(pixel_values, max_length=512)

        # Decode text IDs to string
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print(f"OCR successful for {image_path}. Text length: {len(generated_text)}")
        return generated_text, None # Return text and no error

    except Exception as e:
        print(f"Error during OCR processing for {image_path} with {model_name}: {e}")
        return None, f"An error occurred during OCR: {str(e)}"

# Example usage (optional, for testing)
# if __name__ == "__main__":
#     # Create a dummy image file for testing if needed
#     # test_image_path = "/path/to/your/test_image.png"
#     # text, error = perform_ocr(test_image_path, model_type="printed")
#     # if error:
#     #     print(f"Error: {error}")
#     # else:
#     #     print(f"Extracted Text:\n{text}")
#     pass

