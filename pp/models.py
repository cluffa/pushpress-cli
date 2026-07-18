from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Session:
    client_uuid: str
    user_uuid: str
    company: str
    subdomain: str
    access_token: str
    token_expiration: str
    privileges: list = field(default_factory=list)

    @classmethod
    def from_access_data(cls, d: dict) -> "Session":
        return cls(
            client_uuid=d.get("clientUuid", ""),
            user_uuid=d.get("userUuid", ""),
            company=d.get("company", ""),
            subdomain=d.get("subdomain", ""),
            access_token=d.get("accessToken", ""),
            token_expiration=d.get("tokenExpiration", ""),
            privileges=list(d.get("privileges", [])),
        )

    def to_dict(self) -> dict:
        return {
            "clientUuid": self.client_uuid,
            "userUuid": self.user_uuid,
            "company": self.company,
            "subdomain": self.subdomain,
            "accessToken": self.access_token,
            "tokenExpiration": self.token_expiration,
            "privileges": self.privileges,
        }

    @property
    def is_expired(self) -> bool:
        raw = (self.token_expiration or "").replace("Z", "")
        try:
            exp = datetime.fromisoformat(raw)
        except ValueError:
            return True
        return exp <= datetime.now()
