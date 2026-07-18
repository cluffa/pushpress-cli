import httpx
import respx

from pp.api import client as clientapi
from pp.http import PPClient

BASE = "https://api.pushpress.com"
CU = "client_1"


@respx.mock
def test_gym_strips_event_emitter():
    respx.get(f"{BASE}/v2/client/client/{CU}").mock(
        return_value=httpx.Response(200, json={"company": "G", "_eventEmitter": {"x": 1}})
    )
    out = clientapi.gym(PPClient(token="t"), CU)
    assert out == {"company": "G"}


@respx.mock
def test_settings_passes_type_and_name():
    route = respx.get(f"{BASE}/v2/client/client/{CU}/setting").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    clientapi.settings(PPClient(token="t"), CU, type="core", name="primary_color")
    req = route.calls.last.request
    assert req.url.params["type"] == "core"
    assert req.url.params["name"] == "primary_color"
