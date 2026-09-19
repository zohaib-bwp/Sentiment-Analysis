import numpy as np
from model_loader import load_model

# ---------------------------
# Load model
# ---------------------------
model, vectorizer, model_source, errors = load_model()

print("✅ Model loaded from:", model_source)
print("Vectorizer:", vectorizer)

# ---------------------------
# Test data
# ---------------------------
test_data = [
    ("I love this product", "positive"),
    ("Excellent service", "positive"),
    ("Worst experience ever", "negative"),
    ("I hate this app", "negative"),
    ("Absolutely fantastic", "positive"),
    ("Very bad quality", "negative"),
]

def normalize(pred):
    """
    Safely extract string sentiment from any output type
    """
    # If numpy array → take first element
    if isinstance(pred, np.ndarray):
        pred = pred[0]

    # If list/tuple → take first element
    if isinstance(pred, (list, tuple)):
        pred = pred[0]

    # Convert to string safely
    return str(pred).strip().lower()

correct = 0

print("\n--- Predictions ---\n")

for text, actual in test_data:
    pred = model.predict([text])
    predicted = normalize(pred)

    if predicted == actual:
        correct += 1

    print(f"Text      : {text}")
    print(f"Predicted : {predicted}")
    print(f"Actual    : {actual}")
    print("-" * 40)

accuracy = correct / len(test_data)
print(f"\n🎯 Accuracy: {accuracy * 100:.2f}%")
