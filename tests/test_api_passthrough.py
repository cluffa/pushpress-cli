import httpx
import respx

from pp.api import graphql, raw
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_graphql_posts_query_and_vars():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"__typename": "Query"}})
    )
    out = graphql.query(PPClient(token="t"), "{__typename}", {"a": 1})
    assert out["data"]["__typename"] == "Query"
    body = route.calls.last.request.content.decode()
    assert '"query"' in body and '"variables"' in body


@respx.mock
def test_raw_get():
    respx.get(f"{BASE}/v2/anything").mock(return_value=httpx.Response(200, json={"z": 9}))
    assert raw.get(PPClient(token="t"), "/v2/anything") == {"z": 9}
