from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..auth.oidc import get_tokens, keycloak_openid

router = APIRouter()


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    tokens = await get_tokens(form_data)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user_info": keycloak_openid.userinfo(tokens["access_token"]),
    }
