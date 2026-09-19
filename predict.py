"""
Diagnostic script to test your sentiment analysis model
Run this to see what's happening with your predictions
"""

import re
from model_loader import load_model
import numpy as np

def analyze_keywords(text):
    """Count positive and negative keywords"""
    text_lower = text.lower()
    
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
        'love', 'best', 'perfect', 'outstanding', 'brilliant', 'superb',
        'enjoyed', 'like', 'favorite', 'recommended', 'beautiful', 'awesome'
    ]
    
    negative_words = [
        'bad', 'worst', 'terrible', 'awful', 'horrible', 'poor', 'hate',
        'disappointing', 'waste', 'boring', 'dull', 'weak', 
        'failed', 'failure', 'useless', 'pathetic', 'annoying'
    ]
    
    pos_found = []
    neg_found = []
    
    for word in positive_words:
        matches = re.findall(rf'\b{word}\b', text_lower)
        if matches:
            pos_found.append((word, len(matches)))
    
    for word in negative_words:
        matches = re.findall(rf'\b{word}\b', text_lower)
        if matches:
            neg_found.append((word, len(matches)))
    
    return pos_found, neg_found

def test_prediction(text):
    """Test prediction on given text"""
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS DIAGNOSTIC")
    print("="*60)
    
    # Load model
    print("\n[1] Loading model...")
    model, vectorizer, model_source, errors = load_model()
    
    if errors:
        print("⚠️  Warnings:")
        for e in errors:
            print(f"   - {e}")
    
    print(f"✓ Model loaded: {model_source}")
    
    # Analyze text
    print(f"\n[2] Analyzing text (length: {len(text)} chars)")
    print(f"First 200 chars: {text[:200]}...")
    
    # Keyword analysis
    print("\n[3] Keyword Analysis:")
    pos_words, neg_words = analyze_keywords(text)
    
    print(f"   Positive keywords found: {sum(count for _, count in pos_words)}")
    if pos_words:
        for word, count in sorted(pos_words, key=lambda x: x[1], reverse=True)[:5]:
            print(f"      - '{word}': {count} times")
    
    print(f"   Negative keywords found: {sum(count for _, count in neg_words)}")
    if neg_words:
        for word, count in sorted(neg_words, key=lambda x: x[1], reverse=True)[:5]:
            print(f"      - '{word}': {count} times")
    
    # Model prediction
    print("\n[4] Model Prediction:")
    
    try:
        if vectorizer:
            if hasattr(vectorizer, "texts_to_sequences"):
                from tensorflow.keras.preprocessing.sequence import pad_sequences
                seq = vectorizer.texts_to_sequences([text])
                X = pad_sequences(seq, maxlen=200)
                pred = model.predict(X, verbose=0)
            else:
                X = vectorizer.transform([text])
                pred = model.predict(X)
        else:
            pred = model.predict([text])
        
        value = float(np.squeeze(pred))
        print(f"   Raw prediction value: {value}")
        
        if 0 <= value <= 1:
            positive_prob = value * 100
            negative_prob = (1 - value) * 100
            print(f"   Positive: {positive_prob:.1f}%")
            print(f"   Negative: {negative_prob:.1f}%")
            
            if positive_prob > negative_prob:
                print(f"   → Sentiment: POSITIVE 😊")
            else:
                print(f"   → Sentiment: NEGATIVE 😞")
        else:
            print(f"   ⚠️  Unexpected prediction range: {value}")
            
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
    
    print("\n" + "="*60)

# Test samples
if __name__ == "__main__":
    # Test 1: Clearly positive
    print("\n🧪 TEST 1: Clearly Positive Review")
    test_prediction("This movie was absolutely amazing! I loved every minute. Great acting, wonderful story, perfect!")
    
    # Test 2: Clearly negative
    print("\n🧪 TEST 2: Clearly Negative Review")
    test_prediction("This was the worst movie I've ever seen. Terrible acting, awful plot, complete waste of time!")
    
    # Test 3: Mixed (should be close to 50-50)
    print("\n🧪 TEST 3: Mixed Review")
    test_prediction("The movie had some good scenes and great effects, but the story was weak and boring. Some parts were enjoyable, others were terrible.")
    
    # Test 4: Your file content sample
    print("\n🧪 TEST 4: Sample from your file")
    print("Enter a sample of text from your file (or press Enter to skip):")
    sample = input("> ")
    
    if sample.strip():
        test_prediction(sample)
    
    print("\n✅ Diagnostic complete!")
    print("\nNEXT STEPS:")
    print("1. Check if model predictions match keyword analysis")
    print("2. If model is always predicting one class, it may need retraining")
    print("3. Use the improved app.py which uses hybrid approach")
    print("4. Consider training a new model with more balanced data")