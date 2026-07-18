from pp.errors import AuthError, NotFoundError, PPError


def test_to_dict_omits_none():
    e = AuthError("no token")
    assert e.to_dict() == {"error": "no token", "code": "auth_required"}
    assert e.exit_code == 3


def test_to_dict_includes_detail_and_hint():
    e = NotFoundError("missing", detail="id=1", hint="check the id")
    assert e.to_dict() == {
        "error": "missing",
        "code": "not_found",
        "detail": "id=1",
        "hint": "check the id",
    }
    assert e.exit_code == 4


def test_base_defaults():
    e = PPError("boom")
    assert e.code == "error" and e.exit_code == 1
