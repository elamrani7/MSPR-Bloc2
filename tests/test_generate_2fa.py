import base64
import importlib.util
import json
from pathlib import Path

import pyotp


ROOT_DIR = Path(__file__).resolve().parents[1]
HANDLER_PATH = ROOT_DIR / "functions" / "generate-2fa" / "handler.py"


def load_handler():
    spec = importlib.util.spec_from_file_location("generate_2fa_handler", HANDLER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_totp_secret_returns_non_empty_secret():
    handler = load_handler()

    secret = handler.generate_totp_secret()

    assert secret


def test_generate_totp_secret_is_compatible_with_pyotp():
    handler = load_handler()

    secret = handler.generate_totp_secret()
    code = pyotp.TOTP(secret).now()

    assert len(code) == 6
    assert code.isdigit()


def test_build_totp_uri_contains_username_issuer_and_secret():
    handler = load_handler()
    secret = "JBSWY3DPEHPK3PXP"

    uri = handler.build_totp_uri("testuser", secret)

    assert "testuser" in uri
    assert "issuer=COFRAP" in uri
    assert f"secret={secret}" in uri


def test_generate_qr_code_base64_returns_png_base64():
    handler = load_handler()

    qr_code = handler.generate_qr_code_base64("otpauth://totp/COFRAP:testuser")
    decoded = base64.b64decode(qr_code)

    assert qr_code
    assert decoded.startswith(b"\x89PNG")


def test_qr_code_data_url_starts_with_png_prefix():
    handler = load_handler()

    data_url = handler.build_qr_code_data_url("abc123")

    assert data_url.startswith("data:image/png;base64,")


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


def test_handle_returns_404_when_user_does_not_exist(monkeypatch):
    handler = load_handler()

    monkeypatch.setattr(handler, "update_user_totp_secret", lambda username, secret: 0)

    response = json.loads(handler.handle('{"username": "missing-user"}'))

    assert response["status_code"] == 404
    assert response["error"] == "User not found"


def test_handle_accepts_valid_username_with_mocked_database(monkeypatch):
    handler = load_handler()
    calls = {}

    def fake_update(username, secret):
        calls["username"] = username
        calls["secret"] = secret
        return 1

    monkeypatch.setattr(handler, "update_user_totp_secret", fake_update)

    response = json.loads(handler.handle('{"username": "testuser"}'))

    assert response["username"] == "testuser"
    assert response["secret"] == calls["secret"]
    assert response["qr_code"]
    assert response["qr_code_data_url"].startswith("data:image/png;base64,")
    assert response["message"] == "2FA generated successfully"


def test_update_totp_query_updates_secret_without_password_hash():
    handler = load_handler()
    executed = {}

    class FakeCursor:
        rowcount = 1

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

    updated_rows = handler.update_user_totp_secret(
        "testuser",
        "SECRET",
        connection=FakeConnection(),
    )

    query = " ".join(executed["query"].split()).upper()
    assert "TOTP_SECRET = %S" in query
    assert "PASSWORD_HASH" not in query
    assert "UPDATED_AT = NOW()" in query
    assert executed["params"] == ("SECRET", "testuser")
    assert executed["committed"] is True
    assert updated_rows == 1
