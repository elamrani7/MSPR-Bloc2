# MSPR Bloc 2 - COFRAP

PoC serverless basé sur Kubernetes/K3S, OpenFaaS, PostgreSQL, des fonctions Python et un frontend React.

## Setup local rapide

Rendre les scripts exécutables :

```bash
chmod +x scripts/*.sh
```

Vérifier les outils installés :

```bash
./scripts/check-env.sh
```

Démarrer PostgreSQL local avec Docker et appliquer le schéma :

```bash
./scripts/start-postgres-local.sh
```

Sur Windows PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-postgres-local.ps1
```

Se connecter à PostgreSQL :

```bash
docker exec -it cofrap-postgres psql -U cofrap -d cofrapdb
```

Vérifier la table `users` dans `psql` :

```sql
\dt
\d users
```

Installer les dépendances Python dans un environnement virtuel :

```bash
./scripts/install-python-deps.sh
```

Pour le guide complet, voir [docs/setup-local.md](docs/setup-local.md).

Note Windows : les scripts `scripts/*.sh` sont prévus pour Bash. Utiliser Ubuntu/WSL ou Git Bash, ou les scripts PowerShell `scripts/*.ps1`. Si Docker affiche une erreur sur `dockerDesktopLinuxEngine`, ouvrir Docker Desktop et attendre que le moteur Linux soit démarré avant de relancer les commandes.
