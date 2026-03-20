import json

config_path = 'data/cmd_config.json'

with open(config_path, 'r', encoding='utf-8-sig') as f:
    config = json.load(f)

# Update Kimi (moonshot) to be disabled
for p in config.get('provider', []):
    if p['id'] == 'twopixel-moonshot':
        p['enable'] = False
        print("Disabled moonshot")

# Ensure Qwen source exists
qwen_source_exists = False
for s in config.get('provider_sources', []):
    if s['id'] == 'twopixel-qwen_source':
        qwen_source_exists = True
        break

if not qwen_source_exists:
    config['provider_sources'].append({
      "id": "twopixel-qwen_source",
      "provider": "dashscope",
      "type": "openai_chat_completion",
      "provider_type": "chat_completion",
      "key": [""],
      "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "timeout": 120,
      "proxy": "",
      "custom_headers": {}
    })
    print("Added Qwen source")

# Ensure GLM source exists
glm_source_exists = False
for s in config.get('provider_sources', []):
    if s['id'] == 'twopixel-glm_source':
        glm_source_exists = True
        break

if not glm_source_exists:
    config['provider_sources'].append({
      "id": "twopixel-glm_source",
      "provider": "zhipu",
      "type": "zhipu_chat_completion",
      "provider_type": "chat_completion",
      "key": [""],
      "api_base": "https://open.bigmodel.cn/api/paas/v4",
      "timeout": 120,
      "proxy": "",
      "custom_headers": {}
    })
    print("Added GLM source")

# Ensure providers for Qwen and GLM exist, and update models
expected_providers = {
    'twopixel-deepseek': 'deepseek-chat',
    'twopixel-gemini': 'gemini-3-pro-preview', # or latest
    'twopixel-qwen': 'qwen-max',
    'twopixel-glm': 'glm-4-plus'
}

provider_sources_mapping = {
    'twopixel-qwen': 'twopixel-qwen_source',
    'twopixel-glm': 'twopixel-glm_source'
}

for pid, pmodel in expected_providers.items():
    found = False
    for p in config.get('provider', []):
        if p['id'] == pid:
            p['model'] = pmodel
            p['enable'] = True
            found = True
            print(f"Updated {pid} to model {pmodel}")
            break
    if not found:
        config['provider'].append({
            "id": pid,
            "model": pmodel,
            "enable": True,
            "provider_source_id": provider_sources_mapping.get(pid, ""),
            "modalities": [],
            "custom_extra_body": {}
        })
        print(f"Added provider {pid} with model {pmodel}")

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("Config updated successfully.")
