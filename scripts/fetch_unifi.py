import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY = os.environ.get('UNIFI_API_KEY')
BASE_URL = 'https://api.ui.com/v1'

if not API_KEY:
    print("ERROR: UNIFI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    'X-API-Key': API_KEY,
    'Accept': 'application/json',
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
        print(f"  ✗ HTTP {e.code} for {endpoint}: {e.read().decode()}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}", file=sys.stderr)
        return None

print("Fetching from UniFi Site Manager API...")
hosts   = api_get('hosts')
devices = api_get('devices')
sites   = api_get('sites')

output = {
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'source':  'UniFi Site Manager API v1',
    'hosts':   hosts,
    'devices': devices,
    'sites':   sites,
}

os.makedirs('data', exist_ok=True)
with open('data/live-data.json', 'w') as f:
    json.dump(output, f, indent=2)

device_count = len((devices or {}).get('data', []))
print(f"Done — {device_count} devices saved to data/live-data.json")

