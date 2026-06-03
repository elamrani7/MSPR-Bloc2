import json
import os
from datetime import datetime, timezone

import bcrypt
import psycopg2
import pyotp


MAX_CREDENTIAL_AGE_DAYS = 183


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cofrapdb"),
        user=os.getenv("DB_USER", "cofrap"),
        password=os.getenv("DB_PASSWORD", "cofrap2024"),
    )


def parse_request(req):
    if isinstance(req, bytes):
        req = req.decode("utf-8")

    if not req:
        raise ValueError("Request body must be a valid JSON object")

    try:
        data = json.loads(req.body)
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must be a valid JSON object") from exc

    if not isinstance(data, dict):
        raise ValueError("Request body must be a valid JSON object")

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    # On accepte plusieurs noms possibles pour faciliter l'appel depuis le frontend.
    otp_code = str(
        data.get("otp_code")
        or data.get("totp_code")
        or data.get("code_2fa")
        or data.get("code")
        or ""
    ).strip()

    if not username:
        raise ValueError("username is required")

    if not password:
        raise ValueError("password is required")

    if not otp_code:
        raise ValueError("otp_code is required")

    return username, password, otp_code


def error_response(message, status_code):
    return json.dumps(
        {
            "authenticated": False,
            "error": message,
            "status_code": status_code,
        }
    )


def success_response(username):
    return json.dumps(
        {
            "authenticated": True,
            "username": username,
            "message": "Authentication successful",
            "status_code": 200,
        }
    )


def normalize_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    return None


def is_expired(generated_at, updated_at, max_age_days=MAX_CREDENTIAL_AGE_DAYS):
    now = datetime.now(timezone.utc)

    password_generated_at = normalize_datetime(generated_at)
    totp_updated_at = normalize_datetime(updated_at)

    if password_generated_at is None or totp_updated_at is None:
        return True

    password_age_days = (now - password_generated_at).days
    totp_age_days = (now - totp_updated_at).days

    return password_age_days > max_age_days or totp_age_days > max_age_days


def get_user_by_username(username, connection=None):
    owns_connection = connection is None
    conn = connection or get_db_connection()

    query = """
        SELECT id, username, password_hash, totp_secret, generated_at, updated_at, expired
        FROM users
        WHERE username = %s;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
            row = cursor.fetchone()
    finally:
        if owns_connection:
            conn.close()

    return row


def mark_user_as_expired(username, connection=None):
    owns_connection = connection is None
    conn = connection or get_db_connection()

    query = """
        UPDATE users
        SET expired = TRUE,
            updated_at = NOW()
        WHERE username = %s;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns_connection:
            conn.close()


def verify_password(password, password_hash):
    if not password_hash:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def verify_totp_code(otp_code, totp_secret):
    if not totp_secret:
        return False

    totp = pyotp.TOTP(totp_secret)

    # valid_window=1 accepte aussi le code juste avant/après la fenêtre actuelle.
    # C'est utile car l'utilisateur peut avoir quelques secondes de décalage.
    return totp.verify(otp_code, valid_window=1)


def authenticate_user(username, password, otp_code, connection=None):
    owns_connection = connection is None
    conn = connection or get_db_connection()

    try:
        user = get_user_by_username(username, conn)

        if user is None:
            return error_response("User not found", 404)

        user_id, db_username, password_hash, totp_secret, generated_at, updated_at, expired = user

        if expired:
            return error_response(
                "Credentials expired. Please regenerate password and 2FA.",
                403,
            )

        if is_expired(generated_at, updated_at):
            mark_user_as_expired(username, conn)
            return error_response(
                "Credentials expired. Please regenerate password and 2FA.",
                403,
            )

        if not verify_password(password, password_hash):
            return error_response("Invalid username or password", 401)

        if not verify_totp_code(otp_code, totp_secret):
            return error_response("Invalid 2FA code", 401)

        return success_response(db_username)

    except Exception:
        return error_response("Database error while authenticating user", 500)

    finally:
        if owns_connection:
            conn.close()


def handle(req, context):
    try:
        username, password, otp_code = parse_request(req)
    except ValueError as exc:
        return error_response(str(exc), 400)

    return authenticate_user(username, password, otp_code)