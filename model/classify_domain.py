import pickle
import sys
import math
import pandas as pd

# We need to replicate the feature extraction logic exactly as in training
def entropy(s):
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy

def extract_features(domain):
    features = {}
    features['length'] = len(domain)
    features['num_digits'] = sum(c.isdigit() for c in domain)
    features['entropy'] = entropy(domain)
    features['num_dots'] = domain.count('.')
    suspicious_keywords = ['ad', 'track', 'analytic', 'pixel', 'stats', 'count', 'click', 'offer', 'sale']
    features['has_keyword'] = 1 if any(k in domain for k in suspicious_keywords) else 0
    vowels = "aeiou"
    num_vowels = sum(1 for c in domain.lower() if c in vowels)
    num_cons = sum(1 for c in domain.lower() if c.isalpha() and c not in vowels)
    features['vowel_ratio'] = num_vowels / (num_cons + 1)
    
    # Return as DataFrame for the model
    return pd.DataFrame([features])

def main():
    if len(sys.argv) < 2:
        print("Usage: python classify_domain.py <domain_name>")
        # Interactive mode
        while True:
            domain = input("\nEnter domain to classify (or 'q' to quit): ").strip()
            if domain == 'q':
                break
            classify(domain)
    else:
        domain = sys.argv[1]
        classify(domain)

def classify(domain):
    try:
        with open('dns_classifier.pkl', 'rb') as f:
            clf = pickle.load(f)
    except FileNotFoundError:
        print("Error: Model file 'dns_classifier.pkl' not found. Train the model first.")
        return

    features = extract_features(domain)
    prediction = clf.predict(features)[0]
    probabilities = clf.predict_proba(features)[0]
    
    # probabilities is [prob_class_0, prob_class_1]. 
    # We need to map to labels. The classes_ attribute stores the label order.
    # Usually alphabetical: 'ad', 'safe' -> index 0 is 'ad', index 1 is 'safe'
    
    confidence = max(probabilities)
    
    print(f"\nDomain: {domain}")
    print(f"Prediction: {prediction.upper()}")
    print(f"Confidence: {confidence:.2f}")

if __name__ == '__main__':
    main()
