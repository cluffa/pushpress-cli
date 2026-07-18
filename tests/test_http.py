import httpx
import pytest
import respx

from pp.http import PPClient
from pp.errors import AuthError, NotFoundError, UpstreamError, NetworkError

BASE = "https://api.pushpress.com"


@respx.mock
def test_get_sends_bearer_and_parses():
    route = respx.get(f"{BASE}/v2/thing").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    client = PPClient(token="tok123")
    assert client.get("/v2/thing") == {"ok": True}
    assert route.calls.last.request.headers["authorization"] == "Bearer tok123"


@respx.mock
def test_401_maps_to_auth_error():
    respx.get(f"{BASE}/v2/x").mock(return_value=httpx.Response(401, json={}))
    with pytest.raises(AuthError):
        PPClient(token="t").get("/v2/x")


@respx.mock
def test_404_maps_to_not_found():
    respx.get(f"{BASE}/v2/x").mock(return_value=httpx.Response(404, json={}))
    with pytest.raises(NotFoundError):
        PPClient(token="t").get("/v2/x")


@respx.mock
def test_500_maps_to_upstream():
    respx.get(f"{BASE}/v2/x").mock(return_value=httpx.Response(503, text="down"))
    with pytest.raises(UpstreamError):
        PPClient(token="t").get("/v2/x")


@respx.mock
def test_network_error_maps():
    respx.get(f"{BASE}/v2/x").mock(side_effect=httpx.ConnectError("boom"))
    with pytest.raises(NetworkError):
        PPClient(token="t").get("/v2/x")
