# =============================================================================
# dev-start.ps1 — Universal Dev-Hub Development Startup Script
# =============================================================================
# USAGE: From the Dev-Hub root: .\scripts\dev-start.ps1
# This script:
#   1. Checks prerequisites
#   2. Starts Docker infrastructure
#   3. Prints status and quick access URLs
# =============================================================================

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Universal Dev-Hub — Starting Development Environment  " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Check Docker is running ----------------------------------------
Write-Host "[1/3] Checking Docker..." -ForegroundColor Yellow
try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker not running" }
    Write-Host "      Docker is running." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# --- Step 2: Start infrastructure services ----------------------------------
Write-Host "[2/3] Starting PostgreSQL and MinIO containers..." -ForegroundColor Yellow
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

docker compose up -d 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: docker compose failed. Check docker-compose.yml and .env file." -ForegroundColor Red
    exit 1
}

# Wait for services to become healthy
Write-Host "      Waiting for services to be healthy (up to 30s)..." -ForegroundColor Yellow
$maxWait = 30
$elapsed = 0
while ($elapsed -lt $maxWait) {
    $pgHealth = docker inspect devhub-postgres --format "{{.State.Health.Status}}" 2>&1
    $minioHealth = docker inspect devhub-minio --format "{{.State.Health.Status}}" 2>&1
    if ($pgHealth -eq "healthy" -and $minioHealth -eq "healthy") {
        break
    }
    Start-Sleep -Seconds 2
    $elapsed += 2
}

# --- Step 3: Print container status -----------------------------------------
Write-Host "[3/3] Container Status:" -ForegroundColor Yellow
docker compose ps
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  DEVELOPMENT ENVIRONMENT READY                         " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Infrastructure:" -ForegroundColor White
Write-Host "    PostgreSQL   → localhost:5432      (DB: devhub_db)" -ForegroundColor Gray
Write-Host "    MinIO API    → http://localhost:9000" -ForegroundColor Gray
Write-Host "    MinIO Console→ http://localhost:9001  (login: minioadmin)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Application Services (start manually):" -ForegroundColor White
Write-Host "    BFF          → cd backend/bff    && uvicorn main:app --port 8000 --reload" -ForegroundColor Gray
Write-Host "    Identity     → cd backend/services/identity && uvicorn main:app --port 8001 --reload" -ForegroundColor Gray
Write-Host "    Snippet Eng  → cd backend/services/snippet_engine && python main.py" -ForegroundColor Gray
Write-Host "    Auto Worker  → cd backend/services/automation_worker && uvicorn main:app --port 8003 --reload" -ForegroundColor Gray
Write-Host "    Blob Service → cd backend/services/blob_service && uvicorn main:app --port 8004 --reload" -ForegroundColor Gray
Write-Host "    Analytics    → cd backend/services/analytics && uvicorn main:app --port 8005 --reload" -ForegroundColor Gray
Write-Host "    Frontend     → cd frontend && npm run dev   (→ http://localhost:3000)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Stop Infrastructure: docker compose down" -ForegroundColor DarkGray
Write-Host "  Wipe ALL data:       docker compose down -v  (CAUTION)" -ForegroundColor DarkRed
Write-Host ""
