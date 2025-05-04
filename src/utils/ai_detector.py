# /home/ubuntu/ai_content_detector/src/utils/ai_detector.py

import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch.nn.functional as F

# Dictionary to cache loaded models and tokenizers
detector_cache = {}

def load_detector_model(model_name="roberta-large-openai-detector"):
    """Loads the specified RoBERTa detector model and tokenizer, caching them."""
    if model_name in detector_cache:
        return detector_cache[model_name]

    print(f"Loading AI detector model: {model_name}...")
    try:
        tokenizer = RobertaTokenizer.from_pretrained(model_name)
        model = RobertaForSequenceClassification.from_pretrained(model_name)
        # Check if CUDA is available and move model to GPU if possible
        if torch.cuda.is_available():
            print("CUDA available, moving detector model to GPU.")
            model.to("cuda")
        else:
            print("CUDA not available, using CPU for detector.")
        detector_cache[model_name] = (tokenizer, model)
        print(f"Model {model_name} loaded successfully.")
        return tokenizer, model
    except Exception as e:
        # Fallback or alternative model could be specified here if needed
        print(f"Error loading AI detector model {model_name}: {e}")
        print("Please ensure the model identifier is correct and you have internet access.")
        # Example alternative: \"Hello-SimpleAI/chatgpt-detector-roberta\"
        # For now, we fail if the primary model doesn\"t load.
        return None, None

def detect_ai_content(text):
    """Detects AI-generated content in the given text using the RoBERTa model."""
    model_name = "roberta-large-openai-detector"
    tokenizer, model = load_detector_model(model_name)

    if not tokenizer or not model:
        return None, f"Failed to load AI detector model: {model_name}"

    if not text or not text.strip():
        return None, "Input text cannot be empty."

    print(f"Analyzing text (length: {len(text)}) for AI content...")
    try:
        # Tokenize the input text
        # RoBERTa has a max sequence length (often 512). Handle longer texts if necessary.
        # For now, we truncate. A better approach might involve chunking.
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        # Move inputs to GPU if model is on GPU
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        # Perform inference
        with torch.no_grad():
            logits = model(**inputs).logits

        # Apply softmax to get probabilities
        probabilities = F.softmax(logits, dim=-1)

        # Assuming the model outputs probabilities for [Real, Fake] or [Human, AI]
        # We need to confirm the label mapping for "roberta-large-openai-detector"
        # Based on common detectors, let's assume label 0 = Human/Real, label 1 = AI/Fake
        # It's CRUCIAL to verify this assumption.
        ai_prob = probabilities[0][1].item() # Probability of being AI-generated
        human_prob = probabilities[0][0].item() # Probability of being Human-written

        # Determine the predicted label
        predicted_label_id = torch.argmax(probabilities, dim=-1).item()
        label = "AI" if predicted_label_id == 1 else "Human"

        print(f"Analysis complete. Predicted: {label}, AI Probability: {ai_prob:.4f}")

        # Return detailed results
        result = {
            "prediction": label, # "AI" or "Human"
            "ai_probability": ai_prob, # Probability score for AI
            "human_probability": human_prob # Probability score for Human
        }
        return result, None # Return result and no error

    except Exception as e:
        print(f"Error during AI content detection: {e}")
        return None, f"An error occurred during AI detection: {str(e)}"

# Example usage (optional, for testing)
# if __name__ == \"__main__\":
#     test_text_human = "This is a sample text written by a human author to test the detection capabilities."
#     test_text_ai = "The integration of artificial intelligence into various sectors has led to significant advancements in efficiency and automation, reshaping traditional workflows."
#
#     print("Testing Human Text:")
#     result_human, error_human = detect_ai_content(test_text_human)
#     if error_human:
#         print(f"Error: {error_human}")
#     else:
#         print(result_human)
#
#     print("\nTesting AI Text:")
#     result_ai, error_ai = detect_ai_content(test_text_ai)
#     if error_ai:
#         print(f"Error: {error_ai}")
#     else:
#         print(result_ai)
#     pass

