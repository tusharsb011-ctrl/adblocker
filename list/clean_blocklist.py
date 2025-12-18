import sqlite3
import os
import sys

def clean_blocklist(input_file, db_path=None):
    """
    Remove IP addresses from beginning of lines in the blocklist
    and save the domains to a SQLite database.
    """
    
    # Default DB path: ../database/dns_filter.db relative to this script
    if db_path is None:
        db_path = '../database/dns_filter.db'
    

    print(f"[*] Processing {input_file} -> DB: {db_path}")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"[+] Connected to database.")
    except sqlite3.Error as e:
        print(f"[-] Database error: {e}")
        return

    extracted_count = 0
    domains_to_insert = []
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                original = line.strip()
                
                # Skip empty lines and comments
                if not original or original.startswith('#'):
                    continue
                
                parts = original.split()
                domain = None
                
                # Check if line starts with IP address (e.g., "0.0.0.0 example.com")
                if len(parts) >= 2:
                    first_part = parts[0]
                    # Check if first part is an IP-like string
                    if first_part in ['0.0.0.0', '127.0.0.1'] or first_part.count('.') == 3:
                        domain = parts[1]
                    else:
                        # Maybe the first part is the domain?
                        # But usually blocklists are "IP domain" or just "domain"
                        # If it doesn't look like an IP, assume it's the domain if it has a dot
                        if '.' in first_part:
                            domain = first_part
                elif len(parts) == 1:
                    # Single word, assume it's the domain
                    if '.' in parts[0]:
                        domain = parts[0]
                
                if domain:
                    # Clean potential trailing comments or whitespace
                    domain = domain.strip()
                    domains_to_insert.append((domain,))
                    
                    # Batch insert every 10,000 to save memory
                    if len(domains_to_insert) >= 10000:
                        cursor.executemany('INSERT OR IGNORE INTO blocked (domain) VALUES (?)', domains_to_insert)
                        conn.commit()
                        extracted_count += len(domains_to_insert)
                        domains_to_insert = []
                        print(f"[*] Processed {extracted_count} domains...", end='\r')

        # Insert remaining
        if domains_to_insert:
            cursor.executemany('INSERT OR IGNORE INTO blocked (domain) VALUES (?)', domains_to_insert)
            conn.commit()
            extracted_count += len(domains_to_insert)

        print(f"\n[+] Successfully finished. Total unique domains in DB: {extracted_count}")
        
        # Verify count in DB
        cursor.execute('SELECT COUNT(*) FROM blocked')
        db_count = cursor.fetchone()[0]
        print(f"[+] Total rows in 'blocked' table: {db_count}")

    except Exception as e:
        print(f"[-] Error processing file: {e}")
    finally:
        conn.close()
#this issue is here
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_blocklist.py <input_blocklist_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    print("[*] Using fixed DB path.")
    
    clean_blocklist(input_file)
