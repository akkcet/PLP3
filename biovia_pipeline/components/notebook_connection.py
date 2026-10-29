"""
Biovia Pipeline Pilot - Notebook Connection Component
Production-ready Python implementation.

Supports:
    1. Existing Notebook Session Token
    2. Username/Password authentication
"""

import base64
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger("biovia_pipeline.notebook_connection")


@dataclass
class NotebookConnectionObject:
    """
    Equivalent of the PLP Notebook Connection object.
    """

    connection_name: str
    server_url: str
    api_endpoint: str
    auth_method: str
    username: Optional[str]
    session_token: str
    ria_token: Optional[str] = None
    api_version: str = "25.1"
    additional_headers: Dict[str, str] = field(default_factory=dict)
    raw_connection_hash: Dict[str, Any] = field(default_factory=dict)
    session: Optional[requests.Session] = None
    def to_hash_string(self) -> str:
        payload = json.dumps(self.raw_connection_hash)
        return base64.b64encode(
            payload.encode("utf-8")
        ).decode("utf-8")

@dataclass
class NotebookConnectionConfig:
    """
    Configuration parameters corresponding to PLP Notebook Connection arguments.
    """
    connection_name: str = "NotebookConnection"
    server_url: str = "https://notebook.corp.internal/eln"
    authentication_method: str = "Use Notebook Session Token"
    username: Optional[str] = None
    password: Optional[str] = None
    session_token: Optional[str] = None
    additional_headers: Dict[str, str] = field(default_factory=dict)
    api_version: str = "25.1"
    mock_mode: bool = False

def notebook_connection(
    connection_name: str = "NotebookConnection",
    server_url: str = "https://notebook.unilever.com",
    authentication_method: str = "Use Notebook Session Token",
    username: Optional[str] = None,
    password: Optional[str] = None,
    session_token: Optional[str] = None,
    timeout: int = 30,
) -> NotebookConnectionObject:
    """
    Create a Notebook connection object.

    Authentication options:
        Use Notebook Session Token
        Use Username and Password Parameters
    """

    server_url = server_url.rstrip("/")
    api_endpoint = f"{server_url}/api/v1"

    token = session_token
    headers: Dict[str, str] = {}

    #
    # Option 1 - Existing Notebook Session Token
    #
    if (
        authentication_method
        == "Use Notebook Session Token"
    ):

        if not token:
            raise ValueError(
                "Session token must be supplied "
                "when using "
                "'Use Notebook Session Token'."
            )

    #
    # Option 2 - Username/Password Login
    #
    elif (
        authentication_method
        == "Use Username and Password Parameters"
    ):

        if not username:
            raise ValueError(
                "Username is required."
            )

        if not password:
            raise ValueError(
                "Password is required."
            )

        login_url = (
            f"{server_url}/NotebookLoginService/"
            "rpc/notebookloginservice.svc/Login"
        )

        payload = {
            "username": username,
            "password": password,
        }

        session = requests.Session()

        response = session.post(
            login_url,
            json=payload,
            timeout=timeout,
            verify=True,
        )

        response.raise_for_status()

        data = json.loads(
            response.content.decode("utf-8-sig")
        )

        #
        # Expected BIOVIA response:
        # {
        #   "Content": {
        #       "Token": "xxxxx"
        #   }
        # }
        #
        token = (
            data.get("Content", {})
                .get("Token")
        )

        if not token:
            raise RuntimeError(
                f"Token not found in "
                f"Notebook response: {data}"
            )

        cookies = {
            cookie.name: cookie.value
            for cookie in session.cookies
        }

        if "AuthorizationEln" in cookies:
            headers["AuthorizationEln"] = (
                cookies["AuthorizationEln"]
            )

    else:
        raise ValueError(
            f"Unsupported authentication method: "
            f"{authentication_method}"
        )

    conn_hash = {
        "API Endpoint": api_endpoint,
        "Authentication Method":
            "Use Notebook Session Token",
        "Username": username,
        "Session Token": token,
        "RIA Token": f"ria_{token}",
        "API Version": "25.1",
        **headers,
    }

    connection_object = NotebookConnectionObject(
        connection_name=connection_name,
        server_url=server_url,
        api_endpoint=api_endpoint,
        auth_method="Use Notebook Session Token",
        username=username,
        session_token=token,
        ria_token=f"ria_{token}",
        api_version="25.1",
        additional_headers=headers,
        raw_connection_hash=conn_hash,
        session=session
    )

    logger.info(
        "Notebook Connection established: %s",
        server_url,
    )

    return connection_object


# if __name__ == "__main__":

#     #
#     # Example 1 - Existing Session Token
#     #

#     conn = notebook_connection(
#         connection_name="NotebookConnection",
#         server_url="https://notebook.unilever.com",
#         authentication_method=
#             "Use Notebook Session Token",
#         username="arun.khuntia",
#         session_token="your_session_token_here",
#     )

#     print(conn)
#     print(conn.session_token)
#     print(conn.additional_headers)
#     print(conn.to_hash_string())

    
    #Example 2 - Login with username/password
    
# conn = notebook_connection(
#     server_url="https://notebook.unilever.com",
#     authentication_method=
#         "Use Username and Password Parameters",
#     username="arun.khuntia",
#     password="Pogoanaisha321!",
# )
# print(conn)
# print(conn.session_token)
# print(conn.additional_headers)
# print(conn.to_hash_string())
# print(conn.session.cookies.get_dict())
# print(conn.session.cookies)
# for c in conn.session.cookies:
#     print(c.name, "=", c.value)
# resp = conn.session.get(
#     "https://notebook.unilever.com/api/v1/experiments/EXP-26-BP7567?$format=json&$expand=simplesections"
# )

# print(resp.status_code)
# print(resp.text)