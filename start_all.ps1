$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "     Starting Universal Dev-Hub Stack        " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start Docker Containers (Postgres, MinIO)
Write-Host "Starting Docker Infrastructure..." -ForegroundColor Green
docker compose up -d

# 2. Define the Python Microservices
$services = @(
    @{ Name="Identity Service";   Path="backend\services\identity";          Port=8001; Command="uvicorn main:app --port 8001 --reload" },
    @{ Name="Snippet Engine";     Path="backend\services\snippet_engine";    Port=8002; Command="python main.py" },
    @{ Name="Automation Worker";  Path="backend\services\automation_worker"; Port=8003; Command="uvicorn main:app --port 8003 --reload" },
    @{ Name="Blob Service";       Path="backend\services\blob_service";      Port=8004; Command="uvicorn main:app --port 8004 --reload" },
    @{ Name="Analytics Service";  Path="backend\services\analytics";         Port=8005; Command="uvicorn main:app --port 8005 --reload" },
    @{ Name="API Gateway (BFF)";  Path="backend\bff";                        Port=8000; Command="uvicorn main:app --port 8000 --reload" }
)

# 3. Boot Each Python Microservice in a New Window
foreach ($service in $services) {
    Write-Host "Spawning $($service.Name) (Port $($service.Port))..." -ForegroundColor Yellow
    
    $windowTitle = "Dev-Hub: $($service.Name) - Port $($service.Port)"
    # Using 'cmd /c title' so the window name tells us which service is inside.
    $command = "cmd /c title '$windowTitle'; Write-Host 'Booting $($service.Name)...' -ForegroundColor Cyan; cd $($service.Path); if (Test-Path .\.venv\Scripts\activate.ps1) { . .\.venv\Scripts\activate.ps1; $($service.Command) } else { Write-Host 'VENV NOT FOUND! Did you run python -m venv .venv and pip install?' -ForegroundColor Red; Start-Sleep 15 }"
    
    Start-Process powershell.exe -ArgumentList "-NoExit","-Command", $command -WindowStyle Normal
    Start-Sleep -Seconds 1 # small delay so they stagger opening
}

# 4. Boot the Next.js Frontend
Write-Host "Spawning Next.js Frontend (Port 3000)..." -ForegroundColor Yellow
$frontendTitle = "Dev-Hub: Frontend - Port 3000"
$frontendCommand = "cmd /c title '$frontendTitle'; Write-Host 'Booting Next.js UI...' -ForegroundColor Cyan; cd frontend; npm run dev"
Start-Process powershell.exe -ArgumentList "-NoExit","-Command", $frontendCommand -WindowStyle Normal

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "     All services have been launched!        " -ForegroundColor Green
Write-Host "         http://localhost:3000               " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
