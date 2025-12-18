import socket
import sqlite3
import time
from dnslib import DNSRecord, DNSHeader, RR, QTYPE, A, AAAA
from datetime import datetime
from functools import lru_cache
import subprocess
import webbrowser
import time
from threading import Thread

# Configuration
LISTEN_IP = "0.0.0.0"
DNS_PORT = 53
UPSTREAM_DNS = ("8.8.8.8", 53)
SINKHOLE_IP = "0.0.0.0"
BLOCKLIST_FILE = "blocklist.txt"
DB_FILE = "database/dns_filter.db"



def get_blocked_count():
    """Get count of blocked domains from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM blocked')
        count = c.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"[!] Error reading database: {e}")
        return 0

@lru_cache(maxsize=10000)
def is_blocked_cached(domain):
    """Check if domain is blocked (with caching)"""
    domain = domain.lower().rstrip('.')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    parts = domain.split('.')
    domains_to_check = ['.'.join(parts[i:]) for i in range(len(parts))]
    
    placeholders = ','.join('?' * len(domains_to_check))
    c.execute(f'SELECT domain FROM blocked WHERE domain IN ({placeholders}) LIMIT 1', 
              domains_to_check)
    
    result = c.fetchone()
    conn.close()
    
    return result is not None

def is_blocked(domain):
    """Check if domain should be blocked"""
    return is_blocked_cached(domain)

def log_query(client_ip, domain, query_type, action, response_time):
    """Log DNS query to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO queries 
                     (client_ip, domain, query_type, action, response_time) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (client_ip, domain, query_type, action, response_time))
        conn.commit()
        conn.close()
    except Exception as e:
        pass  # Don't crash if logging fails

def query_upstream(data):
    """Forward DNS query to upstream server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    
    try:
        start_time = time.time()
        sock.sendto(data, UPSTREAM_DNS)
        response, _ = sock.recvfrom(4096)
        response_time = int((time.time() - start_time) * 1000)
        return response, response_time
    except:
        return None, 0
    finally:
        sock.close()

def create_sinkhole_response(request):
    """Create DNS response with sinkhole IP"""
    reply = DNSRecord(
        DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
        q=request.q
    )
    
    qname = str(request.q.qname)
    qtype = request.q.qtype
    
    if qtype == QTYPE.A:
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(SINKHOLE_IP), ttl=60))
    elif qtype == QTYPE.AAAA:
        reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA("::"), ttl=60))
    
    return reply.pack()

def handle_dns_request(data, client_address):
    """Process incoming DNS request"""
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]
        client_ip = client_address[0]
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_blocked(qname):
            print(f"[{timestamp}] BLOCKED: {client_ip:15} → {qname}")
            log_query(client_ip, qname, qtype, "blocked", 0)
            return create_sinkhole_response(request)
        
        response, response_time = query_upstream(data)
        
        if response:
            print(f"[{timestamp}] ALLOWED: {client_ip:15} → {qname} ({response_time}ms)")
            log_query(client_ip, qname, qtype, "allowed", response_time)
            return response
        else:
            return None
            
    except Exception:
        return None

def start_dns_filter():
    """Start the DNS filtering server"""
    domain_count = get_blocked_count()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((LISTEN_IP, DNS_PORT))
        
        print("\n" + "="*60)
        print("DNS FILTERING SERVER (With Logging)")
        print("="*60)
        print(f"Listening on:     {LISTEN_IP}:{DNS_PORT}")
        print(f"Upstream DNS:     {UPSTREAM_DNS[0]}")
        print(f"Sinkhole IP:      {SINKHOLE_IP}")
        print(f"Database:         {DB_FILE}")
        print(f"Blocked domains:  {domain_count:,}")
        print(f"Logging:          ENABLED")
        print("="*60)
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                data, addr = sock.recvfrom(512)
                response = handle_dns_request(data, addr)
                
                if response:
                    try:
                        sock.sendto(response, addr)
                    except OSError:
                        pass
                    
            except KeyboardInterrupt:
                print("\n\n[+] Server stopped")
                break
            except Exception:
                continue
                
    except PermissionError:
        print("\n[!] ERROR: Need sudo/Administrator")
    except OSError as e:
        print(f"\n[!] ERROR: {e}")
    finally:
        sock.close()


def start_server():
    """Start web server and open dashboard"""
    print("Starting web server on port 8000...")
    print("Press Ctrl+C to stop\n")
    
    # Open browser after 2 seconds
    time.sleep(2)
    webbrowser.open("http://localhost:8000/dashboard.html")
    
    # Run the command
    subprocess.run(["python", "-m", "http.server", "8000"])



if __name__ == "__main__":
    web_thread = Thread(target=start_server, daemon=True)
    web_thread.start()

    start_dns_filter()
    
