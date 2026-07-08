# MSPR Bloc 2 - COFRAP

PoC serverless base sur Kubernetes/K3S, OpenFaaS, PostgreSQL, des fonctions Python et un frontend React.

## Setup local rapide

Rendre les scripts executables :

```bash
chmod +x scripts/*.sh
```

Verifier les outils installes :

```bash
./scripts/check-env.sh
```

Demarrer PostgreSQL local avec Docker et appliquer le schema :

```bash
./scripts/start-postgres-local.sh
```

Sur Windows PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-postgres-local.ps1
```

Se connecter a PostgreSQL :

```bash
docker exec -it cofrap-postgres psql -U cofrap -d cofrapdb
```

Verifier la table `users` dans `psql` :

```sql
\dt
\d users
```

Installer les dependances Python dans un environnement virtuel :

```bash
./scripts/install-python-deps.sh
```

## Fonctions Python

Les fonctions OpenFaaS Python sont dans :

- `functions/generate-password`
- `functions/generate-2fa`

Installer les dependances globales :

```bash
pip install -r requirements.txt
```

Lancer les tests unitaires :

```bash
pytest -v
```

Tester `generate-password` localement :

```bash
python -c "from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-password/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle('{\"username\":\"testuser\"}'))"
```

Tester `generate-2fa` localement :

```bash
python -c "from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-2fa/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle('{\"username\":\"testuser\"}'))"
```

Pour le guide complet, voir [docs/setup-local.md](docs/setup-local.md).

Note Windows : les scripts `scripts/*.sh` sont prevus pour Bash. Utiliser Ubuntu/WSL ou Git Bash, ou les scripts PowerShell `scripts/*.ps1`. Si Docker affiche une erreur sur `dockerDesktopLinuxEngine`, ouvrir Docker Desktop et attendre que le moteur Linux soit demarre avant de relancer les commandes.




(.venv) PS C:\Users\a.kuetche1\MSPR-Bloc2> python -c "import json; from importlib.util import spec_from_file_location, module_from_spec; spec = spec_from_file_location('handler', 'functions/generate-password/handler.py'); mod = module_from_spec(spec); spec.loader.exec_module(mod); print(mod.handle(json.dumps({'username':'testuser'})))"
{"username": "testuser", "password": ",6vV2K7d9[=K&GD/7sOKyf1s", "message": "Password generated successfully"}


MOT_DE_PASSE_ADMIN_OPENFASS = WME3PdHqR01SOac6xJyTQrvemsb8flC4

wsl -d Ubuntu


### identifiants azure de youssef
      # DB_HOST: pg-mspr-cofrap-8804.postgres.database.azure.com
      # DB_PORT: "5432"
      # DB_NAME: cofrapdb
      # DB_USER: pgadmin
      # DB_PASSWORD: "123admin"

#### identifiants local avec docker
      # DB_HOST: host.docker.internal
      # DB_PORT: "15432"
      # DB_NAME: cofrapdb
      # DB_USER: cofrap
      # DB_PASSWORD: cofrap2024
      # TOTP_ENCRYPTION_KEY: "EtpyrflbCOoNb2hQGX40atgrZdxK5F_X0_erjRx_K7s="


### commande pour lancer mon Backend
kubectl port-forward -n openfaas svc/gateway 8082:8080