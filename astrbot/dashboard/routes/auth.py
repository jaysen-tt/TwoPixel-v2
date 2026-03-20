import asyncio
import datetime
import os

import aiohttp
import jwt
from quart import request

from .route import Response, Route, RouteContext


class AuthRoute(Route):
    def __init__(self, context: RouteContext) -> None:
        super().__init__(context)
        self.routes = {
            "/auth/login": ("POST", self.login),
            "/auth/signup": ("POST", self.signup),
            "/auth/forgot-password": ("POST", self.forgot_password),
            "/auth/account/edit": ("POST", self.edit_account),
        }
        self.register_routes()

    async def login(self):
        post_data = await request.json
        input_username = str(post_data.get("username", "")).strip()
        input_password = str(post_data.get("password", "")).strip()
        if "@" not in input_username:
            return Response().error("请使用邮箱登录").__dict__
        if not input_password:
            return Response().error("请输入密码").__dict__
        supabase_auth_payload = await self._supabase_sign_in(
            input_username,
            input_password,
        )
        if not supabase_auth_payload:
            await asyncio.sleep(1)
            return Response().error("用户名或密码错误").__dict__
        result = {
            "token": self.generate_jwt(input_username),
            "username": input_username,
            "change_pwd_hint": False,
            "supabase_access_token": str(
                supabase_auth_payload.get("access_token", "") or ""
            ),
            "supabase_refresh_token": str(
                supabase_auth_payload.get("refresh_token", "") or ""
            ),
            "supabase_user": supabase_auth_payload.get("user") or {},
        }
        return Response().ok(result).__dict__

    async def signup(self):
        post_data = await request.json
        email = str(post_data.get("email", "")).strip().lower()
        password = str(post_data.get("password", "")).strip()
        if "@" not in email:
            return Response().error("请输入有效邮箱").__dict__
        if len(password) < 6:
            return Response().error("密码长度至少为 6").__dict__
        payload = await self._supabase_sign_up(email, password)
        if not payload:
            return Response().error("注册失败，请稍后重试").__dict__
        access_token = str(payload.get("access_token", "") or "")
        refresh_token = str(payload.get("refresh_token", "") or "")
        user = payload.get("user") if isinstance(payload.get("user"), dict) else {}
        result = {
            "username": email,
            "email": email,
            "supabase_access_token": access_token,
            "supabase_refresh_token": refresh_token,
            "supabase_user": user or {},
        }
        if access_token:
            result["token"] = self.generate_jwt(email)
        return Response().ok(result, "注册成功").__dict__

    async def forgot_password(self):
        post_data = await request.json
        email = str(post_data.get("email", "")).strip().lower()
        if "@" not in email:
            return Response().error("请输入有效邮箱").__dict__
        ok = await self._supabase_send_reset_email(email)
        if not ok:
            return Response().error("重置邮件发送失败，请稍后重试").__dict__
        return (
            Response()
            .ok(
                {"email": email},
                "已发送重置邮件，请检查收件箱",
            )
            .__dict__
        )

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

    async def _supabase_sign_in(self, email: str, password: str) -> dict | None:
        supabase_url, supabase_anon_key = self._supabase_base()
        if not supabase_url or not supabase_anon_key:
            return None
        endpoint = f"{supabase_url}/auth/v1/token?grant_type=password"
        headers = {
            "Content-Type": "application/json",
            "apikey": supabase_anon_key,
        }
        payload = {
            "email": email,
            "password": password,
        }
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    return data if isinstance(data, dict) else None
        except Exception:
            return None

    async def _supabase_sign_up(self, email: str, password: str) -> dict | None:
        supabase_url, supabase_anon_key = self._supabase_base()
        if not supabase_url or not supabase_anon_key:
            return None
        endpoint = f"{supabase_url}/auth/v1/signup"
        headers = {
            "Content-Type": "application/json",
            "apikey": supabase_anon_key,
        }
        payload = {
            "email": email,
            "password": password,
        }
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status not in (200, 201):
                        return None
                    data = await resp.json()
                    return data if isinstance(data, dict) else None
        except Exception:
            return None

    async def _supabase_send_reset_email(self, email: str) -> bool:
        supabase_url, supabase_anon_key = self._supabase_base()
        if not supabase_url or not supabase_anon_key:
            return False
        endpoint = f"{supabase_url}/auth/v1/recover"
        headers = {
            "Content-Type": "application/json",
            "apikey": supabase_anon_key,
        }
        redirect_to = str(
            os.environ.get("TWOPIXEL_SUPABASE_RESET_REDIRECT")
            or os.environ.get("TWOPIXEL_DASHBOARD_URL")
            or "",
        ).strip()
        payload = {"email": email}
        if redirect_to:
            payload["redirect_to"] = redirect_to
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                ) as resp:
                    return resp.status in (200, 201)
        except Exception:
            return False

    async def edit_account(self):
        return Response().error("本地账号已禁用，请使用 Supabase 账户").__dict__

    def generate_jwt(self, username):
        payload = {
            "username": username,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=7),
        }
        dashboard_cfg = self.config.get("dashboard", {})
        jwt_token = dashboard_cfg.get("jwt_secret", None)
        if not jwt_token:
            jwt_token = os.urandom(32).hex()
            dashboard_cfg["jwt_secret"] = jwt_token
            self.config["dashboard"] = dashboard_cfg
        token = jwt.encode(payload, jwt_token, algorithm="HS256")
        return token
