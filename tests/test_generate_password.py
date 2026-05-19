import importlib.util
import json
from pathlib import Path

import bcrypt


ROOT_DIR = Path(__file__).resolve().parents[1]
HANDLER_PATH = ROOT_DIR / "functions" / "generate-password" / "handler.py"


def load_handler():
    spec = importlib.util.spec_from_file_location("generate_password_handler", HANDLER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_password_returns_24_characters():
    handler = load_handler()

    password = handler.generate_password()

    assert len(password) == 24


def test_generate_password_contains_required_character_classes():
    handler = load_handler()

    password = handler.generate_password()

    assert any(char.isupper() for char in password)
    assert any(char.islower() for char in password)
    assert any(char.isdigit() for char in password)
    assert any(char in handler.SPECIAL_CHARACTERS for char in password)


def test_generate_password_returns_different_values():
    handler = load_handler()

    assert handler.generate_password() != handler.generate_password()


def test_hash_password_returns_valid_bcrypt_hash():
    handler = load_handler()
    password = "Example-password-2024!"

    password_hash = handler.hash_password(password)

    assert password_hash.startswith("$2")
    assert bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def test_handle_returns_error_when_username_is_missing():
    handler = load_handler()

    response = json.loads(handler.handle("{}"))

    assert response["status_code"] == 400
    assert "username" in response["error"]


def test_handle_returns_error_when_json_is_invalid():
    handler = load_handler()

    response = json.loads(handler.handle("{invalid-json"))

    assert response["status_code"] == 400
    assert "JSON" in response["error"]


def test_handle_accepts_valid_username_with_mocked_database(monkeypatch):
    handler = load_handler()
    calls = {}

    def fake_upsert(username, password_hash):
        calls["username"] = username
        calls["password_hash"] = password_hash

    monkeypatch.setattr(handler, "upsert_user_password", fake_upsert)

    response = json.loads(handler.handle('{"username": "testuser"}'))

    assert response["username"] == "testuser"
    assert response["message"] == "Password generated successfully"
    assert len(response["password"]) == 24
    assert calls["username"] == "testuser"
    assert calls["password_hash"] != response["password"]
    assert bcrypt.checkpw(
        response["password"].encode("utf-8"),
        calls["password_hash"].encode("utf-8"),
    )


def test_upsert_query_resets_expired_and_updates_generated_at():
    handler = load_handler()
    executed = {}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def execute(self, query, params):
            executed["query"] = query
            executed["params"] = params

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            executed["committed"] = True

        def rollback(self):
            executed["rolled_back"] = True

    handler.upsert_user_password("testuser", "bcrypt-hash", connection=FakeConnection())

    query = " ".join(executed["query"].split()).upper()
    assert "EXPIRED = FALSE" in query
    assert "GENERATED_AT = NOW()" in query
    assert "UPDATED_AT = NOW()" in query
    assert executed["params"] == ("testuser", "bcrypt-hash")
    assert executed["committed"] is True
