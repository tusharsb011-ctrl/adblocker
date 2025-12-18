import pandas as pd
import numpy as np
import pickle
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import collections

def entropy(s):
    """Calculates the Shannon entropy of a string."""
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy

def extract_features(domain):
    """Extracts features from a domain name."""
    features = {}
    
    # 1. Length of domain
    features['length'] = len(domain)
    
    # 2. Number of digits
    features['num_digits'] = sum(c.isdigit() for c in domain)
    
    # 3. Entropy
    features['entropy'] = entropy(domain)
    
    # 4. Number of subdomains (dots)
    features['num_dots'] = domain.count('.')
    
    # 5. Presence of suspicious keywords
    suspicious_keywords = ['ad', 'track', 'analytic', 'pixel', 'stats', 'count', 'click', 'offer', 'sale']
    features['has_keyword'] = 1 if any(k in domain for k in suspicious_keywords) else 0
    
    # 6. Vowel to consonant ratio (ads sometimes have random strings)
    vowels = "aeiou"
    num_vowels = sum(1 for c in domain.lower() if c in vowels)
    num_cons = sum(1 for c in domain.lower() if c.isalpha() and c not in vowels)
    features['vowel_ratio'] = num_vowels / (num_cons + 1) # +1 to avoid div zero

    return features

def train():
    print("Loading dataset...")
    try:
        df = pd.read_csv('dataset.csv')
    except FileNotFoundError:
        print("Error: dataset.csv not found. Run prepare_data.py first.")
        return

    print("Extracting features...")
    features_list = []
    for domain in df['domain']:
        features_list.append(extract_features(str(domain)))
    
    X = pd.DataFrame(features_list)
    y = df['label']
    
    print(f"Training on {len(X)} samples...")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluation
    y_pred = clf.predict(X_test)
    print("\nModel Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Start Saving
    model_filename = 'dns_classifier.pkl'
    with open(model_filename, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Model saved to {model_filename}")

if __name__ == '__main__':
    train()
