$ErrorActionPreference = "Stop"

$ContainerName = "cofrap-postgres"
$PostgresImage = "postgres:15"
$PostgresDb = "cofrapdb"
$PostgresUser = "cofrap"
$PostgresPassword = "cofrap2024"
$HostPort = "5432"
$SqlFile = "infra/db/init.sql"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "MISSING docker: please install Docker before running this script."
    exit 1
}

if (-not (Test-Path $SqlFile)) {
    Write-Host "Missing SQL file: $SqlFile"
    exit 1
}

function Test-ContainerExists {
    docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
}

function Test-ContainerRunning {
    docker ps --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
}

Write-Host "Starting local PostgreSQL container..."

if (Test-ContainerRunning) {
    Write-Host "Container $ContainerName is already running."
}
elseif (Test-ContainerExists) {
    Write-Host "Container $ContainerName exists but is stopped. Restarting it..."
    docker start $ContainerName | Out-Null
}
else {
    Write-Host "Creating container $ContainerName with image $PostgresImage..."
    docker run -d `
        --name $ContainerName `
        -e POSTGRES_DB=$PostgresDb `
        -e POSTGRES_USER=$PostgresUser `
        -e POSTGRES_PASSWORD=$PostgresPassword `
        -p "${HostPort}:5432" `
        $PostgresImage | Out-Null
}

Write-Host "Waiting for PostgreSQL to be ready..."
for ($attempt = 1; $attempt -le 30; $attempt++) {
    docker exec $ContainerName pg_isready -U $PostgresUser -d $PostgresDb *> $null
    if ($LASTEXITCODE -eq 0) {
        break
    }

    if ($attempt -eq 30) {
        Write-Host "PostgreSQL is not ready after 30 seconds."
        exit 1
    }

    Start-Sleep -Seconds 1
}

Write-Host "Applying database schema from $SqlFile..."
docker cp $SqlFile "${ContainerName}:/tmp/init.sql"
docker exec $ContainerName psql -U $PostgresUser -d $PostgresDb -f /tmp/init.sql

Write-Host ""
Write-Host "PostgreSQL local is ready."
Write-Host "Container: $ContainerName"
Write-Host "Database:  $PostgresDb"
Write-Host "User:      $PostgresUser"
Write-Host "Port:      $HostPort"
Write-Host ""
Write-Host "Connect with:"
Write-Host "docker exec -it $ContainerName psql -U $PostgresUser -d $PostgresDb"
