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

# Try multiple possible URL formats
URL_FORMATS = [
    f'https://unifi.ui.com/consoles/{CONSOLE_ID}/proxy/network/integration/v1',
    f'https://unifi.ui.com/api/consoles/{CONSOLE_ID}/proxy/network/integration/v1',
    f'https://unifi.ui.com/consoles/{CONSOLE_ID}/unifi-api/network/integration/v1',
]

if not API_KEY:
    print("ERROR: UNIFI_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    'X-API-Key': API_KEY,
    'Accept':    'application/json',
}

def api_get(base_url, endpoint):
    url = f"{base_url}/{endpoint}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            print(f"  ✓ {endpoint} — {resp.status} ({len(raw)} bytes)")
            if not raw.strip():
                print(f"    WARNING: empty response body")
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ HTTP {e.code} for {url}")
        print(f"    Response: {body[:200]}")
        return None
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON error for {endpoint}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Error for {url}: {e}")
        return None

# Try each URL format until one works
working_base = None
print("Testing URL formats...")
for base in URL_FORMATS:
    print(f"\nTrying: {base}/sites")
    result = api_get(base, 'sites')
    if result is not None:
        working_base = base
        print(f"  → SUCCESS with {base}")
        break

if not working_base:
    print("\nAll URL formats failed — saving empty data", file=sys.stderr)
    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source':  'UniFi Network Integration API v1 (all URLs failed)',
        'sites':   None,
        'devices': None,
        'clients': None,
    }
else:
    print(f"\nFetching full data from {working_base}...")
    sites   = api_get(working_base, 'sites')
    devices = api_get(working_base, 'sites/default/devices')
    clients = api_get(working_base, 'sites/default/clients')

    device_count = len((devices or {}).get('data', []))
    client_count = len((clients or {}).get('data', []))
    print(f"\nResults: {device_count} devices, {client_count} clients")

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source':  f'UniFi Network Integration API v1 — {working_base}',
        'sites':   sites,
        'devices': devices,
        'clients': clients,
    }

os.makedirs('data', exist_ok=True)
output_path = 'data/live-data.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved → {output_path}  ({os.path.getsize(output_path):,} bytes)")
