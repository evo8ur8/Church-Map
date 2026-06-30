"""
fetch_unifi.py
Fetches live device and client data from the UniFi Network Integration API
via the ui.com cloud proxy.

Required secret: UNIFI_API_KEY (set in GitHub repo Settings > Secrets > Actions)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY    = os.environ.get('UNIFI_API_KEY')
CONSOLE_ID = '6C63F89F8851000000000933A63F0000000009B2372B00000000684E9AAE:1564002746'
BASE_URL   = f'https://unifi.ui.com/proxy/consoles/{CONSOLE_ID}/proxy/network/integration/v1'

if not API_KEY:
    print("ERROR: UNIFI_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    'X-API-Key': API_KEY,
    'Accept':    'application/json',
}

def api_get(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            print(f"  ✓ {endpoint} — {resp.status}")
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ HTTP {e.code} for {endpoint}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ✗ Error for {endpoint}: {e}", file=sys.stderr)
        return None

print("Fetching from UniFi Network Integration API (via ui.com proxy)...")

sites   = api_get('sites')
devices = api_get('sites/default/devices')
clients = api_get('sites/default/clients')

# Build output bundle
output = {
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'source':  'UniFi Network Integration API v1 (cloud proxy)',
    'sites':   sites,
    'devices': devices,
    'clients': clients,
}

device_count = len((devices or {}).get('data', []))
client_count = len((clients or {}).get('data', []))
print(f"\nResults: {device_count} devices, {client_count} clients")

os.makedirs('data', exist_ok=True)
output_path = 'data/live-data.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved → {output_path}  ({os.path.getsize(output_path):,} bytes)")
