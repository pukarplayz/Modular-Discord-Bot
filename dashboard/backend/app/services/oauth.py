"""Discord OAuth helpers using httpx for async HTTP requests."""
import httpx
from typing import Dict, Any, List

from app.config import settings


DISCORD_API = "https://discord.com/api"


async def exchange_code(code: str) -> Dict[str, Any]:
    url = f"{DISCORD_API}/oauth2/token"
    data = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "client_secret": settings.DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data, headers=headers)
        r.raise_for_status()
        return r.json()


async def fetch_user(access_token: str) -> Dict[str, Any]:
    url = f"{DISCORD_API}/users/@me"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()


async def fetch_user_guilds(access_token: str) -> List[Dict[str, Any]]:
    url = f"{DISCORD_API}/users/@me/guilds"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
