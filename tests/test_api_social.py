import httpx
import respx

from pp.api import social
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_feed_passes_params():
    route = respx.get(f"{BASE}/v2/social-feed/feedActivity").mock(
        return_value=httpx.Response(200, json={"activities": [], "limit": "5", "offset": "0"})
    )
    social.feed(PPClient(token="t"), "client_1", limit=5, offset=0)
    p = route.calls.last.request.url.params
    assert p["gymId"] == "client_1" and p["limit"] == "5" and p["offset"] == "0"
