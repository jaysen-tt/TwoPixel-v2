import datetime
import hashlib
import json
import random
import re
import uuid
from collections import defaultdict
from pathlib import Path

from astrbot import logger
from astrbot.api import star
from astrbot.api.event import AstrMessageEvent
from astrbot.api.message_components import At, Image, Plain
from astrbot.api.platform import MessageType
from astrbot.api.provider import LLMResponse, Provider, ProviderRequest
from astrbot.core.astrbot_config_mgr import AstrBotConfigManager
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

"""
聊天记忆增强
"""


class LongTermMemory:
    def __init__(self, acm: AstrBotConfigManager, context: star.Context) -> None:
        self.acm = acm
        self.context = context
        self.session_chats = defaultdict(list)
        self.memory_root = Path(get_astrbot_data_path()) / "twopixel_memory"
        self.sessions_root = self.memory_root / "sessions"
        self.daily_root = self.memory_root / "daily"
        self.durable_root = self.memory_root / "durable"
        self.compactions_root = self.memory_root / "compactions"
        self.distilled_root = self.memory_root / "distilled"
        self.sessions_root.mkdir(parents=True, exist_ok=True)
        self.daily_root.mkdir(parents=True, exist_ok=True)
        self.durable_root.mkdir(parents=True, exist_ok=True)
        self.compactions_root.mkdir(parents=True, exist_ok=True)
        self.distilled_root.mkdir(parents=True, exist_ok=True)

    def cfg(self, event: AstrMessageEvent):
        cfg = self.context.get_config(umo=event.unified_msg_origin)
        try:
            max_cnt = int(cfg["provider_ltm_settings"]["group_message_max_cnt"])
        except BaseException as e:
            logger.error(e)
            max_cnt = 300
        image_caption_prompt = cfg["provider_settings"]["image_caption_prompt"]
        image_caption_provider_id = cfg["provider_ltm_settings"].get(
            "image_caption_provider_id"
        )
        image_caption = cfg["provider_ltm_settings"]["image_caption"] and bool(
            image_caption_provider_id
        )
        active_reply = cfg["provider_ltm_settings"]["active_reply"]
        enable_active_reply = active_reply.get("enable", False)
        ar_method = active_reply["method"]
        ar_possibility = active_reply["possibility_reply"]
        ar_prompt = active_reply.get("prompt", "")
        ar_whitelist = active_reply.get("whitelist", [])
        distill_cfg = cfg["provider_ltm_settings"].get("distillation", {})
        heartbeat_cfg = cfg["provider_ltm_settings"].get("heartbeat", {})
        ret = {
            "max_cnt": max_cnt,
            "image_caption": image_caption,
            "image_caption_prompt": image_caption_prompt,
            "image_caption_provider_id": image_caption_provider_id,
            "enable_active_reply": enable_active_reply,
            "ar_method": ar_method,
            "ar_possibility": ar_possibility,
            "ar_prompt": ar_prompt,
            "ar_whitelist": ar_whitelist,
            "distill_enable": bool(distill_cfg.get("enable", True)),
            "distill_max_records": int(distill_cfg.get("max_records", 1200)),
            "distill_retrieval_top_k": int(distill_cfg.get("retrieval_top_k", 8)),
            "distill_min_score": float(distill_cfg.get("min_score", 1.0)),
            "heartbeat_enable": bool(heartbeat_cfg.get("enable", False)),
            "heartbeat_every_minutes": int(heartbeat_cfg.get("every_minutes", 30)),
            "heartbeat_prompt": str(
                heartbeat_cfg.get(
                    "prompt",
                    "Read current context and decide if anything needs attention. If no action is needed, reply HEARTBEAT_OK.",
                )
            ),
            "heartbeat_target": str(heartbeat_cfg.get("target", "last")),
            "heartbeat_ack_max_chars": int(heartbeat_cfg.get("ack_max_chars", 240)),
            "heartbeat_active_hours_enable": bool(
                heartbeat_cfg.get("active_hours", {}).get("enable", False)
            ),
            "heartbeat_active_hours_start": str(
                heartbeat_cfg.get("active_hours", {}).get("start", "08:00")
            ),
            "heartbeat_active_hours_end": str(
                heartbeat_cfg.get("active_hours", {}).get("end", "23:00")
            ),
            "heartbeat_active_hours_timezone": str(
                heartbeat_cfg.get("active_hours", {}).get("timezone", "")
            ),
        }
        return ret

    def _session_key(self, umo: str) -> str:
        return hashlib.sha1(umo.encode("utf-8")).hexdigest()[:16]

    def _session_file(self, umo: str) -> Path:
        return self.sessions_root / f"{self._session_key(umo)}.json"

    def _daily_file(self, umo: str) -> Path:
        day = datetime.datetime.now().strftime("%Y-%m-%d")
        path = self.daily_root / self._session_key(umo)
        path.mkdir(parents=True, exist_ok=True)
        return path / f"{day}.md"

    def _durable_file(self, umo: str) -> Path:
        path = self.durable_root / self._session_key(umo)
        path.mkdir(parents=True, exist_ok=True)
        return path / "MEMORY.md"

    def _compactions_file(self, umo: str) -> Path:
        return self.compactions_root / f"{self._session_key(umo)}.json"

    def _distilled_file(self, umo: str) -> Path:
        return self.distilled_root / f"{self._session_key(umo)}.json"

    def _load_session_lines(self, umo: str, max_cnt: int) -> list[str]:
        file_path = self._session_file(umo)
        if not file_path.exists():
            return []
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            rows = [str(x).strip() for x in data if str(x).strip()]
            return rows[-max_cnt:]
        except Exception as e:
            logger.error(f"加载会话长期记忆失败: {e}")
            return []

    def _save_session_lines(self, umo: str, rows: list[str], max_cnt: int) -> None:
        file_path = self._session_file(umo)
        try:
            file_path.write_text(
                json.dumps(rows[-max_cnt:], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"保存会话长期记忆失败: {e}")

    def _append_daily_line(self, umo: str, line: str) -> None:
        file_path = self._daily_file(umo)
        try:
            with file_path.open("a", encoding="utf-8") as f:
                f.write(line.strip() + "\n")
        except Exception as e:
            logger.error(f"写入每日记忆失败: {e}")

    def _append_compaction_record(
        self, umo: str, summary: str, source_cnt: int
    ) -> None:
        file_path = self._compactions_file(umo)
        payload = {
            "time": datetime.datetime.now().isoformat(),
            "summary": summary,
            "source_count": source_cnt,
        }
        data = []
        if file_path.exists():
            try:
                loaded = json.loads(file_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    data = loaded
            except Exception:
                data = []
        data.append(payload)
        data = data[-120:]
        try:
            file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"写入压缩总结失败: {e}")

    def _load_distilled_records(self, umo: str) -> list[dict]:
        file_path = self._distilled_file(umo)
        if not file_path.exists():
            return []
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [x for x in data if isinstance(x, dict)]
        except Exception as e:
            logger.error(f"读取蒸馏记忆失败: {e}")
            return []

    def _save_distilled_records(
        self, umo: str, rows: list[dict], max_records: int
    ) -> None:
        file_path = self._distilled_file(umo)
        safe_rows = rows[-max_records:]
        try:
            file_path.write_text(
                json.dumps(safe_rows, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"保存蒸馏记忆失败: {e}")

    def _extract_plain_text_from_line(self, line: str) -> str:
        text = str(line or "").strip()
        if not text:
            return ""
        if "]:" in text:
            text = text.split("]:", 1)[1].strip()
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_files_touched(self, text: str) -> list[str]:
        found = re.findall(
            r"(?:/[\w\-.]+)+\.\w+|[\w\-.]+\.(?:py|ts|tsx|js|jsx|json|yaml|yml|md|txt|sh|vue|toml)",
            text,
        )
        files: list[str] = []
        seen = set()
        for item in found:
            x = str(item).strip()
            if not x or x in seen:
                continue
            seen.add(x)
            files.append(x)
            if len(files) >= 8:
                break
        return files

    def _infer_room_assignments(self, text: str) -> list[str]:
        lowered = text.lower()
        rooms: list[str] = []
        if any(
            k in lowered for k in ["代码", "bug", "fix", "debug", "refactor", "compile"]
        ):
            rooms.append("engineering")
        if any(k in lowered for k in ["配置", "config", "env", "setting"]):
            rooms.append("configuration")
        if any(
            k in lowered for k in ["计划", "方案", "roadmap", "milestone", "分阶段"]
        ):
            rooms.append("planning")
        if any(k in lowered for k in ["偏好", "喜欢", "不喜欢", "prefer", "habit"]):
            rooms.append("preference")
        if any(k in lowered for k in ["记住", "remember", "长期记忆", "memory"]):
            rooms.append("memory")
        return rooms[:4]

    def _extract_specific_context(self, text: str) -> list[str]:
        items: list[str] = []
        patterns = [
            r"(deepseek|gemini|moonshot|claude|gpt[\-\w]*)",
            r"(mcp|cron|subagent|planner|executor|tool)",
            r"(错误|报错|失败|成功|超时|timeout|error|failed|success)",
        ]
        seen = set()
        for pattern in patterns:
            for m in re.findall(pattern, text, re.IGNORECASE):
                token = str(m).strip()
                if not token:
                    continue
                token_low = token.lower()
                if token_low in seen:
                    continue
                seen.add(token_low)
                items.append(token_low)
                if len(items) >= 8:
                    return items
        return items

    def _append_distilled_record(
        self,
        umo: str,
        raw_line: str,
        role: str,
        max_records: int,
    ) -> None:
        text = self._extract_plain_text_from_line(raw_line)
        if not text:
            return
        records = self._load_distilled_records(umo)
        digest = hashlib.sha1(f"{role}:{text}".encode("utf-8")).hexdigest()[:20]
        if records and records[-1].get("id") == digest:
            return
        record = {
            "id": digest,
            "ts": datetime.datetime.now().isoformat(),
            "role": role,
            "exchange_core": text[:260],
            "specific_context": self._extract_specific_context(text),
            "thematic_room_assignments": self._infer_room_assignments(text),
            "files_touched": self._extract_files_touched(text),
        }
        records.append(record)
        self._save_distilled_records(umo, records, max_records)

    def _tokenize_for_retrieval(self, text: str) -> list[str]:
        cn_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        en_tokens = re.findall(r"[a-zA-Z0-9_\-./]{2,}", text.lower())
        tokens = cn_tokens + en_tokens
        dedup: list[str] = []
        seen = set()
        for t in tokens:
            x = t.strip()
            if not x or x in seen:
                continue
            seen.add(x)
            dedup.append(x)
        return dedup[:64]

    def _retrieve_distilled_records(
        self,
        umo: str,
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[dict]:
        records = self._load_distilled_records(umo)
        if not records:
            return []
        q_tokens = set(self._tokenize_for_retrieval(query))
        if not q_tokens:
            return records[-top_k:]
        scored: list[tuple[float, dict]] = []
        total = len(records)
        for idx, rec in enumerate(records):
            text = " ".join(
                [
                    str(rec.get("exchange_core") or ""),
                    " ".join(rec.get("specific_context") or []),
                    " ".join(rec.get("thematic_room_assignments") or []),
                    " ".join(rec.get("files_touched") or []),
                ]
            )
            r_tokens = set(self._tokenize_for_retrieval(text))
            if not r_tokens:
                continue
            overlap = len(q_tokens & r_tokens)
            if overlap <= 0:
                continue
            recency = (idx + 1) / max(total, 1)
            score = float(overlap) + recency * 0.8
            if score >= min_score:
                scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in scored[:top_k]]

    def _score_line_for_summary(self, text: str) -> int:
        score = 0
        lowered = text.lower()
        keys = [
            "记住",
            "偏好",
            "喜欢",
            "不喜欢",
            "决定",
            "方案",
            "问题",
            "报错",
            "error",
            "fix",
            "todo",
            "下一步",
            "模型",
            "工具",
            "配置",
        ]
        for key in keys:
            if key in text or key in lowered:
                score += 2
        if len(text) >= 24:
            score += 1
        return score

    def _build_compaction_summary(self, lines: list[str]) -> str:
        cleaned: list[str] = []
        for raw in lines:
            text = str(raw).strip()
            if not text:
                continue
            if "]:" in text:
                text = text.split("]:", 1)[1].strip()
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                cleaned.append(text)
        if not cleaned:
            return "无有效内容。"
        picked: list[str] = []
        seen = set()
        ranked = sorted(
            cleaned,
            key=lambda x: (self._score_line_for_summary(x), len(x)),
            reverse=True,
        )
        for item in ranked:
            short = item[:140]
            if short in seen:
                continue
            seen.add(short)
            picked.append(short)
            if len(picked) >= 6:
                break
        if not picked:
            picked = cleaned[-3:]
        return "；".join(picked)

    def _compact_session_if_needed(self, umo: str, max_cnt: int) -> None:
        rows = self.session_chats[umo]
        if len(rows) <= max_cnt:
            return
        keep_recent = max(40, int(max_cnt * 0.45))
        keep_recent = min(keep_recent, max_cnt)
        compact_target = rows[:-keep_recent]
        if len(compact_target) < 20:
            self.session_chats[umo] = rows[-max_cnt:]
            return
        summary = self._build_compaction_summary(compact_target)
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        summary_line = f"[MemorySummary/{stamp}] 历史对话压缩总结（{len(compact_target)}条）：{summary}"
        self._append_daily_line(umo, summary_line)
        self._append_compaction_record(umo, summary, len(compact_target))
        merged = [summary_line] + rows[-keep_recent:]
        self.session_chats[umo] = merged[-max_cnt:]

    def _load_durable_memories(self, umo: str) -> list[str]:
        file_path = self._durable_file(umo)
        if not file_path.exists():
            return []
        result: list[str] = []
        try:
            for line in file_path.read_text(encoding="utf-8").splitlines():
                text = line.strip()
                if text.startswith("- "):
                    value = text[2:].strip()
                    if value:
                        result.append(value)
        except Exception as e:
            logger.error(f"读取长期偏好记忆失败: {e}")
        return result

    def _save_durable_memories(self, umo: str, memories: list[str]) -> None:
        if not memories:
            return
        file_path = self._durable_file(umo)
        normalized: list[str] = []
        seen = set()
        for item in memories:
            x = str(item).strip()
            if not x:
                continue
            if x in seen:
                continue
            seen.add(x)
            normalized.append(x[:240])
        body = "# TwoPixel Durable Memory\n\n" + "\n".join(
            f"- {x}" for x in normalized[-120:]
        )
        try:
            file_path.write_text(body, encoding="utf-8")
        except Exception as e:
            logger.error(f"保存长期偏好记忆失败: {e}")

    def _extract_durable_candidate(self, user_text: str) -> str | None:
        text = str(user_text or "").strip()
        if not text:
            return None
        lowered = text.lower()
        explicit = re.search(
            r"(记住|记一下|请记住|帮我记住|remember this|remember that)([:：\s]*)?(.*)",
            text,
            re.IGNORECASE,
        )
        if explicit:
            candidate = explicit.group(3).strip() if explicit.group(3) else ""
            if candidate:
                return candidate[:240]
            return text[:240]
        if text.startswith("我喜欢") or text.startswith("我不喜欢"):
            return text[:240]
        if text.startswith("我叫") or text.startswith("我是"):
            return text[:240]
        if "我的偏好" in text or "我习惯" in text:
            return text[:240]
        if "prefer" in lowered or "i like" in lowered or "i dislike" in lowered:
            return text[:240]
        return None

    def _remember_user_preference(self, umo: str, user_text: str) -> None:
        candidate = self._extract_durable_candidate(user_text)
        if not candidate:
            return
        memories = self._load_durable_memories(umo)
        if candidate in memories:
            return
        memories.append(candidate)
        self._save_durable_memories(umo, memories)

    def _ensure_session_loaded(self, umo: str, max_cnt: int) -> None:
        if umo in self.session_chats and self.session_chats[umo]:
            if len(self.session_chats[umo]) > max_cnt:
                self.session_chats[umo] = self.session_chats[umo][-max_cnt:]
            return
        rows = self._load_session_lines(umo, max_cnt)
        self.session_chats[umo] = rows

    def _build_heartbeat_cron_expression(self, every_minutes: int) -> str:
        minutes = max(5, min(55, int(every_minutes)))
        return f"*/{minutes} * * * *"

    async def _ensure_heartbeat_job(self, event: AstrMessageEvent, cfg: dict) -> None:
        if not cfg["heartbeat_enable"]:
            return
        cron_mgr = self.context.cron_manager
        if cron_mgr is None:
            return
        umo = event.unified_msg_origin
        jobs = await cron_mgr.list_jobs("active_agent")
        existed = [
            j
            for j in jobs
            if isinstance(j.payload, dict)
            and j.payload.get("origin") == "heartbeat"
            and j.payload.get("session") == umo
        ]
        heartbeat_payload = {
            "session": umo,
            "sender_id": event.get_sender_id(),
            "note": cfg["heartbeat_prompt"],
            "origin": "heartbeat",
            "heartbeat": {
                "prompt": cfg["heartbeat_prompt"],
                "target": cfg["heartbeat_target"],
                "ack_max_chars": cfg["heartbeat_ack_max_chars"],
                "active_hours": {
                    "enable": cfg["heartbeat_active_hours_enable"],
                    "start": cfg["heartbeat_active_hours_start"],
                    "end": cfg["heartbeat_active_hours_end"],
                    "timezone": cfg["heartbeat_active_hours_timezone"],
                },
            },
        }
        cron_expression = self._build_heartbeat_cron_expression(
            cfg["heartbeat_every_minutes"]
        )
        if not existed:
            await cron_mgr.add_active_job(
                name="twopixel_heartbeat",
                cron_expression=cron_expression,
                payload=heartbeat_payload,
                description="TwoPixel heartbeat",
                enabled=True,
                persistent=True,
                run_once=False,
            )
            return
        primary = existed[0]
        for redundant in existed[1:]:
            await cron_mgr.delete_job(redundant.job_id)
        await cron_mgr.update_job(
            primary.job_id,
            cron_expression=cron_expression,
            payload=heartbeat_payload,
            enabled=True,
            description="TwoPixel heartbeat",
        )

    async def remove_session(self, event: AstrMessageEvent) -> int:
        cnt = 0
        cfg = self.cfg(event)
        self._ensure_session_loaded(event.unified_msg_origin, cfg["max_cnt"])
        if event.unified_msg_origin in self.session_chats:
            cnt = len(self.session_chats[event.unified_msg_origin])
            del self.session_chats[event.unified_msg_origin]
        try:
            file_path = self._session_file(event.unified_msg_origin)
            if file_path.exists():
                file_path.unlink()
            compactions_file = self._compactions_file(event.unified_msg_origin)
            if compactions_file.exists():
                compactions_file.unlink()
            distilled_file = self._distilled_file(event.unified_msg_origin)
            if distilled_file.exists():
                distilled_file.unlink()
        except Exception as e:
            logger.error(f"清理会话长期记忆失败: {e}")
        return cnt

    async def get_image_caption(
        self,
        image_url: str,
        image_caption_provider_id: str,
        image_caption_prompt: str,
    ) -> str:
        if not image_caption_provider_id:
            provider = self.context.get_using_provider()
        else:
            provider = self.context.get_provider_by_id(image_caption_provider_id)
            if not provider:
                raise Exception(f"没有找到 ID 为 {image_caption_provider_id} 的提供商")
        if not isinstance(provider, Provider):
            raise Exception(f"提供商类型错误({type(provider)})，无法获取图片描述")
        response = await provider.text_chat(
            prompt=image_caption_prompt,
            session_id=uuid.uuid4().hex,
            image_urls=[image_url],
            persist=False,
        )
        return response.completion_text

    async def need_active_reply(self, event: AstrMessageEvent) -> bool:
        cfg = self.cfg(event)
        if not cfg["enable_active_reply"]:
            return False
        if event.get_message_type() != MessageType.GROUP_MESSAGE:
            return False

        if event.is_at_or_wake_command:
            # if the message is a command, let it pass
            return False

        if cfg["ar_whitelist"] and (
            event.unified_msg_origin not in cfg["ar_whitelist"]
            and (
                event.get_group_id() and event.get_group_id() not in cfg["ar_whitelist"]
            )
        ):
            return False

        match cfg["ar_method"]:
            case "possibility_reply":
                trig = random.random() < cfg["ar_possibility"]
                return trig

        return False

    async def handle_message(self, event: AstrMessageEvent) -> None:
        datetime_str = datetime.datetime.now().strftime("%H:%M:%S")
        sender_name = (
            getattr(getattr(event, "message_obj", None), "sender", None).nickname
            if getattr(getattr(event, "message_obj", None), "sender", None)
            else "User"
        )
        parts = [f"[{sender_name}/{datetime_str}]: "]
        cfg = self.cfg(event)

        for comp in event.get_messages():
            if isinstance(comp, Plain):
                parts.append(f" {comp.text}")
            elif isinstance(comp, Image):
                if cfg["image_caption"]:
                    try:
                        url = comp.url if comp.url else comp.file
                        if not url:
                            raise Exception("图片 URL 为空")
                        caption = await self.get_image_caption(
                            url,
                            cfg["image_caption_provider_id"],
                            cfg["image_caption_prompt"],
                        )
                        parts.append(f" [Image: {caption}]")
                    except Exception as e:
                        logger.error(f"获取图片描述失败: {e}")
                else:
                    parts.append(" [Image]")
            elif isinstance(comp, At):
                parts.append(f" [At: {comp.name}]")

        plain_parts: list[str] = []
        for comp in event.get_messages():
            if isinstance(comp, Plain):
                text = str(comp.text).strip()
                if text:
                    plain_parts.append(text)
        raw_user_text = " ".join(plain_parts).strip()

        final_message = "".join(parts).strip()
        logger.debug(f"ltm | {event.unified_msg_origin} | {final_message}")
        self._ensure_session_loaded(event.unified_msg_origin, cfg["max_cnt"])
        self.session_chats[event.unified_msg_origin].append(final_message)
        self._compact_session_if_needed(event.unified_msg_origin, cfg["max_cnt"])
        self._save_session_lines(
            event.unified_msg_origin,
            self.session_chats[event.unified_msg_origin],
            cfg["max_cnt"],
        )
        self._append_daily_line(event.unified_msg_origin, final_message)
        if raw_user_text:
            self._remember_user_preference(event.unified_msg_origin, raw_user_text)
        if cfg["distill_enable"]:
            self._append_distilled_record(
                event.unified_msg_origin,
                final_message,
                role="user",
                max_records=cfg["distill_max_records"],
            )
        await self._ensure_heartbeat_job(event, cfg)

    async def on_req_llm(self, event: AstrMessageEvent, req: ProviderRequest) -> None:
        """当触发 LLM 请求前，调用此方法修改 req"""
        cfg = self.cfg(event)
        self._ensure_session_loaded(event.unified_msg_origin, cfg["max_cnt"])
        if event.unified_msg_origin not in self.session_chats:
            return
        chats_str = "\n---\n".join(self.session_chats[event.unified_msg_origin][-80:])
        durable_memories = self._load_durable_memories(event.unified_msg_origin)[-16:]
        distilled_records = []
        if cfg["distill_enable"]:
            query_text = str(req.prompt or event.message_str or "")
            distilled_records = self._retrieve_distilled_records(
                event.unified_msg_origin,
                query=query_text,
                top_k=cfg["distill_retrieval_top_k"],
                min_score=cfg["distill_min_score"],
            )
        durable_section = ""
        if durable_memories:
            durable_section = "TwoPixel Durable Memory:\n" + "\n".join(
                f"- {x}" for x in durable_memories
            )
        distilled_section = ""
        if distilled_records:
            lines = []
            for rec in distilled_records:
                core = str(rec.get("exchange_core") or "").strip()
                if not core:
                    continue
                rooms = ",".join(rec.get("thematic_room_assignments") or [])
                files = ",".join(rec.get("files_touched") or [])
                line = f"- {core}"
                if rooms:
                    line += f" | rooms:{rooms}"
                if files:
                    line += f" | files:{files}"
                lines.append(line)
            if lines:
                distilled_section = "TwoPixel Distilled Memory v1:\n" + "\n".join(lines)
        if cfg["enable_active_reply"]:
            prompt = req.prompt
            preface = ""
            if durable_section:
                preface = durable_section + "\n\n"
            if distilled_section:
                preface += distilled_section + "\n\n"
            req.prompt = (
                f"{preface}You are now in a chatroom. The chat history is as follows:\n{chats_str}"
                f"\nNow, a new message is coming: `{prompt}`. "
                "Please react to it. Only output your response and do not output any other information. "
                "You MUST use the SAME language as the chatroom is using."
            )
            req.contexts = []
        else:
            if req.system_prompt is None:
                req.system_prompt = ""
            if durable_section:
                req.system_prompt += durable_section + "\n"
            if distilled_section:
                req.system_prompt += distilled_section + "\n"
            req.system_prompt += (
                "You are now in a chatroom. The chat history is as follows: \n"
            )
            req.system_prompt += chats_str

    async def after_req_llm(
        self, event: AstrMessageEvent, llm_resp: LLMResponse
    ) -> None:
        cfg = self.cfg(event)
        self._ensure_session_loaded(event.unified_msg_origin, cfg["max_cnt"])
        if llm_resp.completion_text:
            final_message = f"[You/{datetime.datetime.now().strftime('%H:%M:%S')}]: {llm_resp.completion_text}"
            logger.debug(
                f"Recorded AI response: {event.unified_msg_origin} | {final_message}"
            )
            self.session_chats[event.unified_msg_origin].append(final_message)
            self._compact_session_if_needed(event.unified_msg_origin, cfg["max_cnt"])
            self._save_session_lines(
                event.unified_msg_origin,
                self.session_chats[event.unified_msg_origin],
                cfg["max_cnt"],
            )
            self._append_daily_line(event.unified_msg_origin, final_message)
            if cfg["distill_enable"]:
                self._append_distilled_record(
                    event.unified_msg_origin,
                    final_message,
                    role="assistant",
                    max_records=cfg["distill_max_records"],
                )
