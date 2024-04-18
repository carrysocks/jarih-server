import os
from typing import Any, Dict, Optional

from pydantic import BaseSettings


"""
중요 정보
"""


class AppSettings(BaseSettings):
    DEBUG: bool = False
    REDOC_URL: Optional[str] = None
    DOCS_URL: Optional[str] = "/docs"
    TITLE: str = "GBUS"
    VERSION: str = "0.0.1"
    DESCRIPTION: str = "GBUS API Open API Docs"
    DB_URL: str = os.environ["DB_URL"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ALGORITHM: str = os.environ["ALGORITHM"]
    LAMBDA_ENDPOINT: str = os.environ["LAMBDA_ENDPOINT"]

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "redoc_url": self.REDOC_URL,
            "title": self.TITLE,
            "version": self.VERSION,
            "description": self.DESCRIPTION,
            "openapi_url": None,
            "secret_key":self.SECRET_KEY,
            "algorithm":self.ALGORITHM,
            "lambda_endpoint":self.LAMBDA_ENDPOINT
        }
