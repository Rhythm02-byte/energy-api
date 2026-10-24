import os
import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing API token",
    headers={"WWW-Authenticate": "Bearer"},
)


def require_token(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.environ.get("API_TOKEN", "")
    # Fail closed: with no token configured, no request is allowed through.
    if not expected or not authorization:
        raise UNAUTHORIZED

    scheme, _, token = authorization.partition(" ")
    if scheme != "Bearer" or not secrets.compare_digest(token, expected):
        raise UNAUTHORIZED
