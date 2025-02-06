# Models
from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str
    username: str
    roles: list[str]
