from __future__ import annotations


class PPError(Exception):
    code: str = "error"
    exit_code: int = 1

    def __init__(self, message: str, *, detail: str | None = None, hint: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail
        self.hint = hint

    def to_dict(self) -> dict:
        out = {"error": self.message, "code": self.code}
        if self.detail is not None:
            out["detail"] = self.detail
        if self.hint is not None:
            out["hint"] = self.hint
        return out


class UsageError(PPError):
    code = "usage"
    exit_code = 2


class AuthError(PPError):
    code = "auth_required"
    exit_code = 3


class NotFoundError(PPError):
    code = "not_found"
    exit_code = 4


class UpstreamError(PPError):
    code = "upstream_error"
    exit_code = 5


class NetworkError(PPError):
    code = "network_error"
    exit_code = 6
