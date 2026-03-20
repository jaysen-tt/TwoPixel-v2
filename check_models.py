import json
import urllib.request

with open('data/cmd_config.json', 'r', encoding='utf-8-sig') as f:
    config = json.load(f)

for src in config.get('provider_sources', []):
    print(f"Source ID: {src['id']}")
    print(f"Type: {src['type']}")
    print(f"API Base: {src.get('api_base')}")
    print(f"Key: {src.get('key', [''])[0][:10]}...")
    print("---")
