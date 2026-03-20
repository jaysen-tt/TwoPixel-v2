import json

with open('data/cmd_config.json', 'r', encoding='utf-8-sig') as f:
    config = json.load(f)

print("Provider Sources:")
for src in config.get('provider_sources', []):
    print(f" - ID: {src['id']}, Key starts with: {src.get('key', [''])[0][:10]}...")

print("\nProviders:")
for p in config.get('provider', []):
    print(f" - ID: {p['id']}, Model: {p['model']}, Enabled: {p.get('enable')}")
