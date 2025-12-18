import pandas as pd
import random
import re

def load_blocklist(filepath):
    """Parses existing blocklist file to extract ad domains."""
    ad_domains = []
    print(f"Loading blocklist from {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Format is often "0.0.0.0 domain.com" or just "domain.com"
                parts = line.split()
                if len(parts) >= 2 and (parts[0] == '0.0.0.0' or parts[0] == '127.0.0.1'):
                    ad_domains.append(parts[1])
                elif len(parts) == 1:
                     # Some lines might be just domains if it came from a pure list source
                     # But looking at the user's file, it seems to be hosts format mostly or mixed.
                     # Let's assume if it doesn't start with # and looks like a domain, it is one.
                     # But to be safe vs the file I saw, let's verify.
                     # The file I saw had "39: facebook.com" (with line numbers added by view_file, so I ignore those).
                     # The original file likely has lines like "facebook.com" directly or "0.0.0.0 facebook.com"
                     # The 'view_file' tool added line numbers, the file on disk does not have them.
                     domain = parts[0]
                     # Basic filter to ensure it looks like a domain
                     if '.' in domain and not domain.startswith('0.0.0.0') and not domain.startswith('127.0.0.1'):
                         ad_domains.append(domain)
    except Exception as e:
        print(f"Error reading blocklist: {e}")
    return list(set(ad_domains))

def load_safelist(filepath):
    """Parses safelist file."""
    safe_domains = []
    print(f"Loading safelist from {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain:
                    safe_domains.append(domain)
    except Exception as e:
        print(f"Error reading safelist: {e}")
    return list(set(safe_domains))

def prepare_dataset():
    blocklist_path = 'blocklist.txt' # Assuming it's in the parent dir or adjacent, checking path...
    # The user said current active doc is c:\Users\ranjeeta\Desktop\proj with db\list\append_file.py
    # and blocklist was in c:\Users\ranjeeta\Desktop\proj with db\blocklist.txt
    # So if this script is in c:\Users\ranjeeta\Desktop\proj with db\list\, blocklist is at ../blocklist.txt
    
    # Wait, I am writing this to `list/prepare_data.py`. Blocklist is in parent dir.
    blocklist_path = '../blocklist.txt'
    safelist_path = 'safelist.txt'

    ad_domains = load_blocklist(blocklist_path)
    safe_domains = load_safelist(safelist_path)

    print(f"Found {len(ad_domains)} ad domains and {len(safe_domains)} safe domains.")

    # We need to balance the classes somewhat.
    # Ad domains will vastly outnumber safe domains.
    # Let's take all safe domains, and subsample ad domains.
    # If we have very few safe domains (e.g. 100), the model might key on specific features of those 100 too much.
    # Ideally we'd have thousands. But for this demo, we'll work with what we have.
    # Let's take up to 3x the number of safe domains as ad domains to have a bit more variety but not overwhelming.
    
    n_safe = len(safe_domains)
    n_ads_to_keep = min(len(ad_domains), n_safe * 5) # 5:1 ratio max
    
    selected_ads = random.sample(ad_domains, n_ads_to_keep) if n_ads_to_keep < len(ad_domains) else ad_domains

    data = []
    for d in safe_domains:
        data.append({'domain': d, 'label': 'safe'})
    for d in selected_ads:
        data.append({'domain': d, 'label': 'ad'})
    
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    output_file = 'dataset.csv'
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file} with {len(df)} rows.")
    print(df['label'].value_counts())

if __name__ == '__main__':
    prepare_dataset()
