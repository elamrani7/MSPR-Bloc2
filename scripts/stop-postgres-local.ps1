$ErrorActionPreference = "Stop"

$ContainerName = "cofrap-postgres"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "MISSING docker: please install Docker before running this script."
    exit 1
}

$RunningContainer = docker ps --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
$ExistingContainer = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }

if ($RunningContainer) {
    docker stop $ContainerName | Out-Null
    Write-Host "Container $ContainerName stopped."
}
elseif ($ExistingContainer) {
    Write-Host "Container $ContainerName already exists but is not running."
}
else {
    Write-Host "Container $ContainerName does not exist."
}
