"""Authentication routes handling Discord OAuth2 and token issuance."""
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from starlette.responses import RedirectResponse

from app.services import oauth as oauth_svc
from app.services.auth import create_access_token
from app.config import settings

router = APIRouter()


@router.get("/login")
async def login():
    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
        "prompt": "consent",
    }
    url = "https://discord.com/api/oauth2/authorize"
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(f"{url}?{query}")


@router.get("/callback")
async def callback(request: Request, response: Response):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    token_data = await oauth_svc.exchange_code(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    user = await oauth_svc.fetch_user(access_token)
    # fetch guilds but keep raw guilds for frontend filtering
    guilds = await oauth_svc.fetch_user_guilds(access_token)

    # TODO: persist user and guilds in DB

    jwt = create_access_token(subject=str(user["id"]))
    # set token in secure cookie (frontend will use it)
    response = RedirectResponse(url=settings.BACKEND_CORS_ORIGINS[0])
    response.set_cookie("access_token", jwt, httponly=True, secure=(settings.ENV == "production"))
    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url=settings.BACKEND_CORS_ORIGINS[0])
    response.delete_cookie("access_token")
    return response
