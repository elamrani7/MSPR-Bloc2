# Setup local - MSPR Bloc 2 COFRAP

Ce guide installe les outils nécessaires pour développer le PoC en local.
La cible principale est Ubuntu/Linux. Sur Windows, il est recommandé d'utiliser WSL2 avec Ubuntu et Docker Desktop.

## 1. Prérequis

- Un terminal Bash
- Git
- Un compte avec droits `sudo` sur Ubuntu
- Une connexion internet
- Docker Desktop, Docker CE ou Docker Engine fonctionnel

Mettre à jour Ubuntu :

```bash
sudo apt update
sudo apt upgrade -y
```

Installer les outils de base :

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release apt-transport-https
```

## 2. Installer Git

```bash
sudo apt install -y git
git --version
```

## 3. Installer Docker

### Option Ubuntu avec Docker CE

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Autoriser l'utilisateur courant à lancer Docker sans `sudo` :

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

Vérifier :

```bash
docker --version
docker run hello-world
```

### Note Windows/WSL

Installer Docker Desktop, activer l'intégration WSL2, puis vérifier dans Ubuntu/WSL :

```bash
docker --version
docker ps
```

Si vous lancez les commandes depuis PowerShell et obtenez une erreur du type
`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`,
cela signifie généralement que Docker Desktop n'est pas démarré ou que le moteur Linux n'est pas prêt.

Actions à vérifier :

```powershell
docker context ls
docker version
```

Puis :

- ouvrir Docker Desktop ;
- attendre que le statut indique que Docker est démarré ;
- vérifier que Docker utilise les conteneurs Linux ;
- activer l'intégration WSL2 dans Docker Desktop si vous travaillez avec Ubuntu/WSL ;
- relancer ensuite `docker ps`.

Les scripts `scripts/*.sh` sont des scripts Bash. Sur Windows, lancez-les de préférence depuis Ubuntu/WSL ou Git Bash. Depuis PowerShell, ils peuvent ne pas s'exécuter comme attendu selon la configuration du poste.

Des scripts PowerShell sont aussi fournis pour PostgreSQL local :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-postgres-local.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\stop-postgres-local.ps1
```

## 4. Installer kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl
kubectl version --client
```

## 5. Installer k3d pour Kubernetes local

k3d permet de lancer un cluster K3S dans Docker. C'est simple pour un PoC local.

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
k3d version
```

Créer un cluster local si besoin :

```bash
k3d cluster create cofrap-local --agents 1
kubectl get nodes
```

Alternative : installer K3S directement sur Linux avec le script officiel si vous ne voulez pas utiliser k3d.

## 6. Installer Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

## 7. Installer OpenFaaS CLI

```bash
curl -sSL https://cli.openfaas.com | sudo sh
faas-cli version
```

## 8. Installer Python 3.11, pip et venv

Sur Ubuntu récent :

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
python3.11 --version
pip3 --version
```

Installer les dépendances du projet dans un environnement virtuel :

```bash
./scripts/install-python-deps.sh
```

Ou manuellement :

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Dépendances Python utilisées pour le PoC :

- `bcrypt`
- `pyotp`
- `qrcode`
- `psycopg2-binary`
- `pillow`
- `pyjwt`

## 9. Installer Node.js 18+ et npm

Exemple avec NodeSource :

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

## 10. Lancer PostgreSQL local avec Docker

Le projet fournit un script simple pour lancer PostgreSQL 15 avec des identifiants de développement local.

```bash
chmod +x scripts/*.sh
./scripts/start-postgres-local.sh
```

Sur Windows PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-postgres-local.ps1
```

Configuration locale :

- Base : `cofrapdb`
- Utilisateur : `cofrap`
- Mot de passe : `cofrap2024`
- Port : `5432`
- Conteneur : `cofrap-postgres`

Ces valeurs sont destinées au développement local uniquement.

## 11. Appliquer le script SQL

Le script `scripts/start-postgres-local.sh` applique automatiquement :

```bash
infra/db/init.sql
```

Pour l'appliquer manuellement :

```bash
docker cp infra/db/init.sql cofrap-postgres:/tmp/init.sql
docker exec cofrap-postgres psql -U cofrap -d cofrapdb -f /tmp/init.sql
```

## 12. Vérifier la table users

Se connecter à PostgreSQL :

```bash
docker exec -it cofrap-postgres psql -U cofrap -d cofrapdb
```

Dans `psql` :

```sql
\dt
\d users
```

La table `users` doit contenir les colonnes `id`, `username`, `password_hash`, `totp_secret`, `generated_at`, `updated_at` et `expired`.

## 13. Vérifier l'environnement

Lancer le script de contrôle :

```bash
./scripts/check-env.sh
```

Vérifier manuellement les versions :

```bash
git --version
docker --version
kubectl version --client
helm version
faas-cli version
python3 --version
pip3 --version
node --version
npm --version
```

## 14. Arrêter PostgreSQL local

```bash
./scripts/stop-postgres-local.sh
```

Sur Windows PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-postgres-local.ps1
```
