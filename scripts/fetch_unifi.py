Church-Map/
├── .github/
│   └── workflows/
│       └── fetch-unifi-data.yml   ← GitHub Actions reads this
├── scripts/
│   └── fetch_unifi.py             ← workflow calls this
├── data/
│   └── live-data.json             ← auto-created by first run
└── network_map.html               ← your map
