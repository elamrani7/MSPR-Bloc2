import base64
import io
import json
import os

import psycopg2
import pyotp
import qrcode
from cryptography.fernet import Fernet


ISSUER_NAME = "COFRAP"


def get_encryption_key():
    key = os.getenv("TOTP_ENCRYPTION_KEY")

    if not key:
        raise ValueError("TOTP_ENCRYPTION_KEY environment variable is required")

    return key.encode("utf-8")


def encrypt_totp_secret(secret):
    fernet = Fernet(get_encryption_key())
    encrypted_secret = fernet.encrypt(secret.encode("utf-8"))
    return encrypted_secret.decode("utf-8")


def generate_totp_secret():
    return pyotp.random_base32()


def build_totp_uri(username, secret, issuer_name=ISSUER_NAME):
    return pyotp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=issuer_name,
    )


def generate_qr_code_base64(totp_uri):
    image = qrcode.make(totp_uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def build_qr_code_data_url(qr_code_base64):
    return f"data:image/png;base64,{qr_code_base64}"


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cofrapdb"),
        user=os.getenv("DB_USER", "cofrap"),
        password=os.getenv("DB_PASSWORD", "cofrap2024"),
    )


def update_user_totp_secret(username, encrypted_secret, connection=None):
    owns_connection = connection is None
    conn = connection or get_db_connection()

    query = """
        UPDATE users
        SET totp_secret = %s,
            updated_at = NOW()
        WHERE username = %s;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (encrypted_secret, username))
            updated_rows = cursor.rowcount
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns_connection:
            conn.close()

    return updated_rows


def parse_request(req):
    if hasattr(req, "body"):
        body = req.body
    else:
        body = req

    if isinstance(body, bytes):
        body = body.decode("utf-8")

    if not body:
        raise ValueError("Request body must be a valid JSON object")

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must be a valid JSON object") from exc

    if not isinstance(data, dict):
        raise ValueError("Request body must be a valid JSON object")

    username = str(data.get("username", "")).strip()

    if not username:
        raise ValueError("username is required")

    return username


def error_response(message, status_code):
    return json.dumps(
        {
            "error": message,
            "status_code": status_code,
        }
    )


def handle(req, context=None):
    try:
        username = parse_request(req)
    except ValueError as exc:
        return error_response(str(exc), 400)

    try:
        secret = generate_totp_secret()
        encrypted_secret = encrypt_totp_secret(secret)
    except Exception as exc:
        return error_response(f"Error while encrypting 2FA secret: {str(exc)}", 500)

    totp_uri = build_totp_uri(username, secret)
    qr_code = generate_qr_code_base64(totp_uri)
    qr_code_data_url = build_qr_code_data_url(qr_code)

    try:
        updated_rows = update_user_totp_secret(username, encrypted_secret)
    except Exception as exc:
        return error_response(f"Database error while generating 2FA: {str(exc)}", 500)

    if updated_rows == 0:
        return error_response("User not found", 404)

    return json.dumps(
        {
            "username": username,
            "secret": secret,
            "qr_code": qr_code,
            "qr_code_data_url": qr_code_data_url,
            "message": "2FA generated successfully",
        }
    )