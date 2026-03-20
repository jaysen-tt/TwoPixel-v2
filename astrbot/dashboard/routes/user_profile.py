import datetime
import json
import os
from pathlib import Path
import httpx
import asyncio

from quart import g, request

from astrbot.core import DEMO_MODE
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

from .route import Response, Route, RouteContext


class UserProfileRoute(Route):
    def __init__(self, context: RouteContext) -> None:
        super().__init__(context)
        self.routes = {
            "/user/profile": [("GET", self.get_profile), ("POST", self.update_profile)],
        }
        self.profiles_file = (
            Path(get_astrbot_data_path()) / "dashboard_user_profiles.json"
        )
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        self.register_routes()

    def _supabase_base(self) -> tuple[str, str]:
        supabase_url = str(
            os.environ.get("TWOPIXEL_SUPABASE_URL")
            or os.environ.get("VITE_SUPABASE_URL")
            or "https://fusvdsmjvtgoxwmvgsin.supabase.co",
        ).strip()
        supabase_anon_key = str(
            os.environ.get("TWOPIXEL_SUPABASE_ANON_KEY")
            or os.environ.get("VITE_SUPABASE_ANON_KEY")
            or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1c3Zkc21qdnRnb3h3bXZnc2luIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MjAwNjUsImV4cCI6MjA4NDM5NjA2NX0.u2QaDCoWuc1in6xHnv1SKqTL7Ip4XSh7rj_-FiHfkwo",
        ).strip()
        return supabase_url, supabase_anon_key

    def _load_profiles(self) -> dict:
        if not self.profiles_file.exists():
            return {}
        try:
            data = json.loads(self.profiles_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
        return {}

    def _save_profiles(self, profiles: dict) -> None:
        self.profiles_file.write_text(
            json.dumps(profiles, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    async def _fetch_supabase_user(self, access_token: str) -> dict | None:
        supabase_url, supabase_anon_key = self._supabase_base()
        if not supabase_url or not supabase_anon_key or not access_token:
            return None
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": supabase_anon_key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                res = await client.get(
                    f"{supabase_url}/auth/v1/user",
                    headers=headers,
                    timeout=10.0,
                )
                if res.status_code != 200:
                    return None
                data = res.json()
                return data if isinstance(data, dict) else None
        except Exception:
            return None

    async def get_profile(self):
        username = str(getattr(g, "username", "") or "").strip() or "user"
        profiles = self._load_profiles()
        profile = profiles.get(username) if isinstance(profiles, dict) else None
        if not isinstance(profile, dict):
            profile = {}

        sb_token = request.headers.get(
            "X-Supabase-Access-Token"
        ) or request.headers.get("x-supabase-access-token")
        sb_user_id = request.headers.get("X-Supabase-User-Id") or request.headers.get(
            "x-supabase-user-id"
        )
        supabase_user = None
        supabase_url, supabase_anon_key = self._supabase_base()
        debug_enabled = request.args.get("debug") == "1"
        debug_info = {
            "supabase_url": supabase_url,
            "has_supabase_token": bool(sb_token),
            "has_supabase_user_id": bool(sb_user_id),
            "metadata_name": "",
            "metadata_avatar": "",
            "profiles_row_found": False,
        }

        if sb_token:
            try:
                supabase_user = await self._fetch_supabase_user(sb_token)
                if supabase_user and not sb_user_id:
                    sb_user_id = supabase_user.get("id")
                if supabase_user:
                    metadata = supabase_user.get("user_metadata") or {}
                    if isinstance(metadata, dict):
                        name = str(
                            metadata.get("full_name") or metadata.get("name") or ""
                        ).strip()
                        avatar = str(metadata.get("avatar_url") or "").strip()
                        if debug_enabled:
                            debug_info["metadata_name"] = name
                            debug_info["metadata_avatar"] = avatar
                        if name:
                            profile["nickname"] = name
                        if avatar:
                            profile["avatar_url"] = avatar

                if not sb_user_id:
                    raise ValueError("Supabase user id missing")
                async with httpx.AsyncClient() as client:
                    sb_headers = {
                        "apikey": supabase_anon_key,
                        "Authorization": f"Bearer {sb_token}",
                        "Content-Type": "application/json",
                    }
                    res = await client.get(
                        f"{supabase_url}/rest/v1/profiles?id=eq.{sb_user_id}",
                        headers=sb_headers,
                        timeout=10.0,
                    )
                    if res.status_code == 200:
                        rows = res.json()
                        if rows and isinstance(rows, list) and len(rows) > 0:
                            if debug_enabled:
                                debug_info["profiles_row_found"] = True
                            sb_profile = rows[0]
                            if sb_profile.get("username"):
                                profile["nickname"] = sb_profile.get("username")
                            if sb_profile.get("avatar_url"):
                                profile["avatar_url"] = sb_profile.get("avatar_url")
                            profiles[username] = profile
                            self._save_profiles(profiles)
            except Exception:
                pass

        if debug_enabled:
            profile["debug"] = debug_info
        return (
            Response()
            .ok(
                {
                    "username": username,
                    "nickname": str(profile.get("nickname", "") or ""),
                    "avatar_url": str(profile.get("avatar_url", "") or ""),
                    "updated_at": str(profile.get("updated_at", "") or ""),
                }
            )
            .__dict__
        )

    async def update_profile(self):
        if DEMO_MODE:
            return Response().error("You are not permitted in demo mode").__dict__
        username = str(getattr(g, "username", "") or "").strip() or "user"
        post_data = await request.json
        nickname = str(post_data.get("nickname", "") or "").strip()
        avatar_url = str(post_data.get("avatar_url", "") or "").strip()
        if len(nickname) > 64:
            return Response().error("昵称不能超过 64 个字符").__dict__
        if len(avatar_url) > 2_000_000:
            return Response().error("头像数据过大").__dict__

        sb_token = request.headers.get(
            "X-Supabase-Access-Token"
        ) or request.headers.get("x-supabase-access-token")
        sb_user_id = request.headers.get("X-Supabase-User-Id") or request.headers.get(
            "x-supabase-user-id"
        )

        if sb_token:
            try:
                if not sb_user_id:
                    supabase_user = await self._fetch_supabase_user(sb_token)
                    if supabase_user:
                        sb_user_id = supabase_user.get("id")
                supabase_url, supabase_anon_key = self._supabase_base()
                async with httpx.AsyncClient() as client:
                    sb_headers = {
                        "apikey": supabase_anon_key,
                        "Authorization": f"Bearer {sb_token}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",
                    }
                    if sb_user_id:
                        payload = [
                            {
                                "username": nickname,
                                "avatar_url": avatar_url or None,
                                "updated_at": datetime.datetime.now(
                                    datetime.timezone.utc
                                ).isoformat(),
                            }
                        ]
                        res = await client.patch(
                            f"{supabase_url}/rest/v1/profiles?id=eq.{sb_user_id}",
                            headers=sb_headers,
                            json=payload,
                            timeout=10.0,
                        )
                        if res.status_code == 200:
                            rows = res.json()
                            if not rows or len(rows) == 0:
                                payload[0]["id"] = sb_user_id
                                payload[0]["email"] = (
                                    username if "@" in username else None
                                )
                                await client.post(
                                    f"{supabase_url}/rest/v1/profiles",
                                    headers=sb_headers,
                                    json=payload,
                                    timeout=10.0,
                                )

                    auth_meta_headers = {
                        "apikey": supabase_anon_key,
                        "Authorization": f"Bearer {sb_token}",
                        "Content-Type": "application/json",
                    }
                    meta_payload = {
                        "data": {
                            "full_name": nickname,
                            "name": nickname,
                            "avatar_url": avatar_url or None,
                        }
                    }
                    await client.put(
                        f"{supabase_url}/auth/v1/user",
                        headers=auth_meta_headers,
                        json=meta_payload,
                        timeout=10.0,
                    )
            except Exception:
                pass

        profiles = self._load_profiles()
        profiles[username] = {
            "nickname": nickname,
            "avatar_url": avatar_url,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self._save_profiles(profiles)
        return Response().ok(None, "保存成功").__dict__
