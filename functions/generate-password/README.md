# generate-password

OpenFaaS Python function that receives a username, generates a strong 24-character password, hashes it with bcrypt, then inserts or updates the user in PostgreSQL.

The plain password is returned once to the caller and is never stored in the database. Only the bcrypt hash is saved in `users.password_hash`.

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
  "password": "generated_password",
  "message": "Password generated successfully"
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

Start PostgreSQL:

```bash
./scripts/start-postgres-local.sh
```

From PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-postgres-local.ps1
```

Run the handler locally:

```bash
python -c "from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-password/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle('{\"username\":\"testuser\"}'))"
```

## Security reminder

- Password length is exactly 24 characters.
- It contains at least one uppercase letter, one lowercase letter, one digit and one special character.
- Password generation uses Python `secrets`.
- The plain password is not stored in PostgreSQL.
