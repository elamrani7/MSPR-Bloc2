import json
import os
import secrets
import string

import bcrypt
import psycopg2


PASSWORD_LENGTH = 24
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{};:,.?/|"


def generate_password(length=PASSWORD_LENGTH):
    if length < 4:
        raise ValueError("Password length must be at least 4 characters")

    character_sets = [
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        SPECIAL_CHARACTERS,
    ]

    password_chars = [secrets.choice(character_set) for character_set in character_sets]
    all_characters = "".join(character_sets)
    password_chars.extend(
        secrets.choice(all_characters) for _ in range(length - len(password_chars))
    )

    # Shuffle with secrets so the guaranteed character classes are not predictable.
    for index in range(len(password_chars) - 1, 0, -1):
        swap_index = secrets.randbelow(index + 1)
        password_chars[index], password_chars[swap_index] = (
            password_chars[swap_index],
            password_chars[index],
        )

    return "".join(password_chars)


def hash_password(password):
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return password_hash.decode("utf-8")


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cofrapdb"),
        user=os.getenv("DB_USER", "cofrap"),
        password=os.getenv("DB_PASSWORD", "cofrap2024"),
    )


def upsert_user_password(username, password_hash, connection=None):
    owns_connection = connection is None
    conn = connection or get_db_connection()

    query = """
        INSERT INTO users (username, password_hash, generated_at, updated_at, expired)
        VALUES (%s, %s, NOW(), NOW(), FALSE)
        ON CONFLICT (username)
        DO UPDATE SET
            password_hash = EXCLUDED.password_hash,
            generated_at = NOW(),
            updated_at = NOW(),
            expired = FALSE;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (username, password_hash))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns_connection:
            conn.close()


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
    if not username:
        raise ValueError("username is required")

    return username


def error_response(message, status_code):
    return json.dumps({"error": message, "status_code": status_code})


def handle(req, context):
    try:
        username = parse_request(req)
    except ValueError as exc:
        return error_response(str(exc), 400)

    password = generate_password()
    password_hash = hash_password(password)

    try:
        upsert_user_password(username, password_hash)
    except Exception:
        return error_response("Database error while generating password", 500)

    return json.dumps(
        {
            "username": username,
            "password": password,
            "message": "Password generated successfully",
        }
    )
