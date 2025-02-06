import json

import jwt
from fastapi import Depends
from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordRequestForm,
)
from keycloak import KeycloakAuthenticationError, KeycloakOpenID
from pydantic_core import ValidationError

from ...settings.config import config
from ..schemas.token import TokenData
from ..utils.error_handler import (
    format_validation_error_msg,
    handle_error_helper,
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=(
        f"{config.KEYCLOAK_URL}/realms/{config.REALM_NAME}"
        "/protocol/openid-connect/auth"
    ),
    tokenUrl=(
        f"{config.KEYCLOAK_URL}/realms/{config.REALM_NAME}/"
        "protocol/openid-connect/token"
    ),
)

keycloak_openid = KeycloakOpenID(
    server_url=config.KEYCLOAK_URL,
    realm_name=f"{config.REALM_NAME}",
    client_id=f"{config.KEYCLOAK_CLIENT_ID}",
    client_secret_key=f"{config.KEYCLOAK_CLIENT_SECRET}",
)


async def get_tokens(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and retrieve tokens from Keycloak.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing
                                                    the username and password.

    Returns:
        dict: A dictionary containing the tokens from Keycloak.

    Raises:
        HTTPException: If authentication fails, an HTTP 401
                                        error is raised with the error message.
    """
    try:
        token = keycloak_openid.token(
            username=form_data.username,
            password=form_data.password,
            grant_type="password",
        )
        return token
    except KeycloakAuthenticationError as e:
        error = f"{json.loads(e.error_message.decode('utf-8'))['error_description']}"  # noqa: E501
        handle_error_helper(401, f"Login failed. Error: {error}")
        raise

    except Exception as e:
        handle_error_helper(401, f"Login failed. Error: {e}")
        raise


async def validate_token(token: str) -> TokenData:
    """
    Validates a given JWT token and extracts user information.

    Args:
        token (str): The JWT token to be validated.

    Returns:
        TokenData: An object containing the username and roles extracted
                                                            from the token.

    Raises:
        HTTPException: If the token is invalid or missing required claims.
        Exception: For any other server errors.
    """
    try:
        payload = keycloak_openid.decode_token(token)

        username = payload.get("preferred_username")
        roles = payload.get("realm_access", {}).get("roles", [])
        sub = payload.get("sub") or ""

        if not username:
            handle_error_helper(401, "Token missing required claims")
            raise

        return TokenData(username=username, roles=roles, sub=sub)

    except jwt.PyJWTError as e:
        handle_error_helper(401, f"Invalid token: {str(e)}")
        raise

    except ValidationError as e:
        handle_error_helper(400, format_validation_error_msg(e))
        raise

    except Exception as e:
        handle_error_helper(500, f"Server error: {str(e)}")
        raise


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the provided OAuth2 token.

    Args:
        token (str): The OAuth2 token provided by the client.
            Defaults to the token obtained from the `oauth2_scheme` dependency.

    Returns:
        dict: The validated token information if the token is valid.

    Raises:
        HTTPException: If the token is not provided or is invalid,
                                            an HTTP 401 error is raised.
    """
    if not token:
        handle_error_helper(401, "Not authenticated")
        raise
    return await validate_token(token)


def has_role(required_role: str):
    """
    Decorator to check if the current user has the required role.

    Args:
        required_role (str): The role required to access the decorated
                                                                endpoint.

    Returns:
        Callable: A function that checks the user's roles and raises
                            an error if the required role is not present.

    Raises:
        HTTPException: If the user does not have the required role,
                                            a 403 Forbidden error is raised.
    """

    def role_checker(
        token_data: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if (
            not hasattr(token_data, "roles")
            or required_role not in token_data.roles
        ):
            handle_error_helper(403, "Not authorized")
            raise
        return token_data

    return role_checker
