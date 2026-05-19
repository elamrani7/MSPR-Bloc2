# generate-2fa

OpenFaaS Python function that receives a username, generates a TOTP secret, creates a Google Authenticator compatible QR code, stores the secret in PostgreSQL, and returns the QR code to the frontend.

The function expects the user to already exist. The normal flow is:

1. Call `generate-password`.
2. Call `generate-2fa`.

If the user does not exist, the function returns a `404` error response.

## Input

```json
{
  "username": "testuser"
}
```

## Success output

```json
{
  "username": "testuser",
  "secret": "SECRET_BASE32",
  "qr_code": "base64_png",
  "qr_code_data_url": "data:image/png;base64,...",
  "message": "2FA generated successfully"
}
```

## Environment variables

- `DB_HOST` default `localhost`
- `DB_PORT` default `5432`
- `DB_NAME` default `cofrapdb`
- `DB_USER` default `cofrap`
- `DB_PASSWORD` default `cofrap2024`

These defaults are for local development only.

## Local test

Start PostgreSQL and create a user first:

```bash
./scripts/start-postgres-local.sh
python -c "from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-password/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle('{\"username\":\"testuser\"}'))"
```

Run the 2FA handler locally:

```bash
python -c "from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-2fa/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle('{\"username\":\"testuser\"}'))"
```

## QR code

The QR code is generated as PNG, encoded in base64, and returned both as raw base64 and as a `data:image/png;base64,...` data URL. It is compatible with Google Authenticator through the issuer name `COFRAP`.
