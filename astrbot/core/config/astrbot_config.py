import enum
import json
import logging
import os

from astrbot.core.utils.astrbot_path import get_astrbot_data_path

from .default import DEFAULT_CONFIG, DEFAULT_VALUE_MAP

ASTRBOT_CONFIG_PATH = os.path.join(get_astrbot_data_path(), "cmd_config.json")
logger = logging.getLogger("astrbot")


class RateLimitStrategy(enum.Enum):
    STALL = "stall"
    DISCARD = "discard"


class AstrBotConfig(dict):
    """从配置文件中加载的配置，支持直接通过点号操作符访问根配置项。

    - 初始化时会将传入的 default_config 与配置文件进行比对，如果配置文件中缺少配置项则会自动插入默认值并进行一次写入操作。会递归检查配置项。
    - 如果配置文件路径对应的文件不存在，则会自动创建并写入默认配置。
    - 如果传入了 schema，将会通过 schema 解析出 default_config，此时传入的 default_config 会被忽略。
    """

    config_path: str
    default_config: dict
    schema: dict | None

    def __init__(
        self,
        config_path: str = ASTRBOT_CONFIG_PATH,
        default_config: dict = DEFAULT_CONFIG,
        schema: dict | None = None,
    ) -> None:
        super().__init__()

        # 调用父类的 __setattr__ 方法，防止保存配置时将此属性写入配置文件
        object.__setattr__(self, "config_path", config_path)
        object.__setattr__(self, "default_config", default_config)
        object.__setattr__(self, "schema", schema)

        if schema:
            default_config = self._config_schema_to_default_config(schema)

        if not self.check_exist():
            """不存在时载入默认配置"""
            with open(config_path, "w", encoding="utf-8-sig") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
                object.__setattr__(self, "first_deploy", True)  # 标记第一次部署

        with open(config_path, encoding="utf-8-sig") as f:
            conf_str = f.read()
            # Handle UTF-8 BOM if present
            if conf_str.startswith("\ufeff"):
                conf_str = conf_str[1:]
            conf = json.loads(conf_str)

        has_new = self.check_config_integrity(default_config, conf)

        provider_sources = conf.setdefault("provider_sources", [])
        providers = conf.setdefault("provider", [])

        def upsert_provider_source(source_conf: dict) -> None:
            nonlocal has_new
            source_id = source_conf["id"]
            for i, src in enumerate(provider_sources):
                if src.get("id") == source_id:
                    merged = dict(src)
                    merged.update(source_conf)
                    if merged != src:
                        provider_sources[i] = merged
                        has_new = True
                    return
            provider_sources.append(source_conf)
            has_new = True

        def upsert_provider(provider_conf: dict) -> None:
            nonlocal has_new
            provider_id = provider_conf["id"]
            for i, p in enumerate(providers):
                if p.get("id") == provider_id:
                    merged = dict(p)
                    merged.update(provider_conf)
                    if merged != p:
                        providers[i] = merged
                        has_new = True
                    return
            providers.append(provider_conf)
            has_new = True

        def env_key_for(source_id: str) -> str:
            return os.environ.get(
                f"ASTRBOT_KEY_{source_id.upper().replace('-', '_')}",
                "",
            ).strip()

        deepseek_source_id = "twopixel-deepseek_source"
        gemini_source_id = "twopixel-gemini_source"
        gemini_image_source_id = "twopixel-gemini_image_source"
        qwen_source_id = "twopixel-qwen_source"
        glm_source_id = "twopixel-glm_source"

        upsert_provider_source(
            {
                "id": deepseek_source_id,
                "provider": "deepseek",
                "type": "openai_chat_completion",
                "provider_type": "chat_completion",
                "key": [env_key_for(deepseek_source_id)],
                "api_base": "https://api.deepseek.com/v1",
                "timeout": 120,
                "proxy": "",
                "custom_headers": {},
            }
        )
        upsert_provider_source(
            {
                "id": gemini_source_id,
                "provider": "google",
                "type": "googlegenai_chat_completion",
                "provider_type": "chat_completion",
                "key": [env_key_for(gemini_source_id)],
                "api_base": "https://generativelanguage.googleapis.com/",
                "timeout": 120,
                "gm_resp_image_modal": False,
                "gm_native_search": False,
                "gm_native_coderunner": False,
                "gm_url_context": False,
                "gm_safety_settings": {
                    "harassment": "BLOCK_MEDIUM_AND_ABOVE",
                    "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
                    "sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
                    "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
                },
                "proxy": "",
                "custom_headers": {},
            }
        )
        gemini_image_key = env_key_for(gemini_image_source_id) or env_key_for(gemini_source_id)
        upsert_provider_source(
            {
                "id": gemini_image_source_id,
                "provider": "google",
                "type": "googlegenai_chat_completion",
                "provider_type": "chat_completion",
                "key": [gemini_image_key],
                "api_base": "https://generativelanguage.googleapis.com/",
                "timeout": 120,
                "gm_resp_image_modal": True,
                "gm_native_search": False,
                "gm_native_coderunner": False,
                "gm_url_context": False,
                "gm_safety_settings": {
                    "harassment": "BLOCK_MEDIUM_AND_ABOVE",
                    "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
                    "sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
                    "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
                },
                "proxy": "",
                "custom_headers": {},
            }
        )
        upsert_provider_source(
            {
                "id": qwen_source_id,
                "provider": "dashscope",
                "type": "openai_chat_completion",
                "provider_type": "chat_completion",
                "key": [env_key_for(qwen_source_id)],
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "timeout": 120,
                "proxy": "",
                "custom_headers": {},
            }
        )
        upsert_provider_source(
            {
                "id": glm_source_id,
                "provider": "zhipu",
                "type": "zhipu_chat_completion",
                "provider_type": "chat_completion",
                "key": [env_key_for(glm_source_id)],
                "api_base": "https://open.bigmodel.cn/api/paas/v4",
                "timeout": 120,
                "proxy": "",
                "custom_headers": {},
            }
        )

        upsert_provider(
            {
                "id": "twopixel-deepseek",
                "model": "deepseek-chat",
                "enable": True,
                "provider_source_id": deepseek_source_id,
                "modalities": [],
                "custom_extra_body": {},
            }
        )
        upsert_provider(
            {
                "id": "twopixel-gemini",
                "model": "gemini-3-pro-preview",
                "enable": True,
                "provider_source_id": gemini_source_id,
                "modalities": [],
                "custom_extra_body": {},
            }
        )
        upsert_provider(
            {
                "id": "twopixel-gemini-image",
                "model": "nano-banana-pro-preview",
                "enable": True,
                "provider_source_id": gemini_image_source_id,
                "modalities": [],
                "custom_extra_body": {},
            }
        )
        upsert_provider(
            {
                "id": "twopixel-qwen",
                "model": "qwen-max",
                "enable": True,
                "provider_source_id": qwen_source_id,
                "modalities": [],
                "custom_extra_body": {},
            }
        )
        upsert_provider(
            {
                "id": "twopixel-glm",
                "model": "glm-5",
                "enable": True,
                "provider_source_id": glm_source_id,
                "modalities": [],
                "custom_extra_body": {},
            }
        )

        for provider in providers:
            if provider.get("id") == "twopixel-moonshot" and provider.get("enable") is not False:
                provider["enable"] = False
                has_new = True

        for ps in provider_sources:
            source_id = ps.get("id")
            if not source_id:
                continue
            env_key = env_key_for(source_id)
            if env_key and ps.get("key") != [env_key]:
                ps["key"] = [env_key]
                has_new = True

        self.update(conf)
        if has_new:
            self.save_config()

    def _config_schema_to_default_config(self, schema: dict) -> dict:
        """将 Schema 转换成 Config"""
        conf = {}

        def _parse_schema(schema: dict, conf: dict) -> None:
            for k, v in schema.items():
                if v["type"] not in DEFAULT_VALUE_MAP:
                    raise TypeError(
                        f"不受支持的配置类型 {v['type']}。支持的类型有：{DEFAULT_VALUE_MAP.keys()}",
                    )
                if "default" in v:
                    default = v["default"]
                else:
                    default = DEFAULT_VALUE_MAP[v["type"]]

                if v["type"] == "object":
                    conf[k] = {}
                    _parse_schema(v["items"], conf[k])
                elif v["type"] == "template_list":
                    conf[k] = default
                else:
                    conf[k] = default

        _parse_schema(schema, conf)

        return conf

    def check_config_integrity(self, refer_conf: dict, conf: dict, path=""):
        """检查配置完整性，如果有新的配置项或顺序不一致则返回 True"""
        has_new = False

        # 创建一个新的有序字典以保持参考配置的顺序
        new_conf = {}

        # 先按照参考配置的顺序添加配置项
        for key, value in refer_conf.items():
            if key not in conf:
                # 配置项不存在，插入默认值
                path_ = path + "." + key if path else key
                logger.info(f"检查到配置项 {path_} 不存在，已插入默认值 {value}")
                new_conf[key] = value
                has_new = True
            elif conf[key] is None:
                # 配置项为 None，使用默认值
                new_conf[key] = value
                has_new = True
            elif isinstance(value, dict):
                # 递归检查子配置项
                if not isinstance(conf[key], dict):
                    # 类型不匹配，使用默认值
                    new_conf[key] = value
                    has_new = True
                else:
                    # 递归检查并同步顺序
                    child_has_new = self.check_config_integrity(
                        value,
                        conf[key],
                        path + "." + key if path else key,
                    )
                    new_conf[key] = conf[key]
                    has_new |= child_has_new
            else:
                # 直接使用现有配置
                new_conf[key] = conf[key]

        # 检查是否存在参考配置中没有的配置项
        for key in list(conf.keys()):
            if key not in refer_conf:
                path_ = path + "." + key if path else key
                logger.info(f"检查到配置项 {path_} 不存在，将从当前配置中删除")
                has_new = True

        # 顺序不一致也算作变更
        if list(conf.keys()) != list(new_conf.keys()):
            if path:
                logger.info(f"检查到配置项 {path} 的子项顺序不一致，已重新排序")
            else:
                logger.info("检查到配置项顺序不一致，已重新排序")
            has_new = True

        # 更新原始配置
        conf.clear()
        conf.update(new_conf)

        return has_new

    def save_config(self, conf: dict | None = None) -> None:
        if conf is None:
            conf = self

        # Update self if a new conf is provided
        if conf is not self:
            self.clear()
            self.update(conf)

        # Prevent writing environment-injected API keys back to the config file
        conf_to_save = self.copy()
        if "provider_sources" in conf_to_save:
            conf_to_save["provider_sources"] = []
            for ps in self.get("provider_sources", []):
                ps_copy = ps.copy()
                # If the key was loaded from ENV, we should clear it or leave it as "" in the file
                # But to be safe, we just clear all keys in the file and enforce ENV usage
                if "id" in ps_copy:
                    env_key_name = f"ASTRBOT_KEY_{ps_copy['id'].upper().replace('-', '_')}"
                    if os.environ.get(env_key_name) and "key" in ps_copy:
                        ps_copy["key"] = [""]
                conf_to_save["provider_sources"].append(ps_copy)

        with open(self.config_path, "w", encoding="utf-8-sig") as f:
            json.dump(conf_to_save, f, indent=2, ensure_ascii=False)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __delattr__(self, key) -> None:
        try:
            del self[key]
            self.save_config()
        except KeyError:
            raise AttributeError(f"没有找到 Key: '{key}'")

    def __setattr__(self, key, value) -> None:
        self[key] = value

    def check_exist(self) -> bool:
        return os.path.exists(self.config_path)
