# First-time project setup after cloning.
# This script is idempotent: it preserves existing .env settings and .venv.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$envExamplePath = Join-Path $projectRoot ".env.example"
$envPath = Join-Path $projectRoot ".env"
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$devRequirements = Join-Path $projectRoot "requirements-dev.txt"

Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath $envExamplePath -PathType Leaf)) {
    throw "Missing environment template: $envExamplePath"
}

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    Copy-Item -LiteralPath $envExamplePath -Destination $envPath
    Write-Host "[OK] Created .env from .env.example"
}
else {
    Write-Host "[SKIP] .env already exists; existing settings are preserved"
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    Write-Host "[RUN] Creating the .venv virtual environment..."
    & python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create .venv. Verify that the python command is available."
    }
    Write-Host "[OK] Created the .venv virtual environment"
}
else {
    Write-Host "[SKIP] .venv already exists"
}

$envContent = [System.IO.File]::ReadAllText($envPath)
$defaultSecret = 'APP_SECRET_KEY="dev-only-change-me-before-production"'

if ($envContent.Contains($defaultSecret)) {
    $secretKey = (& $venvPython -c "import secrets; print(secrets.token_urlsafe(64))").Trim()
    if ($LASTEXITCODE -ne 0 -or -not $secretKey) {
        throw "Failed to generate APP_SECRET_KEY."
    }

    $envContent = $envContent.Replace(
        $defaultSecret,
        "APP_SECRET_KEY=`"$secretKey`""
    )
    $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($envPath, $envContent, $utf8WithoutBom)
    Write-Host "[OK] Generated a new APP_SECRET_KEY"
}
else {
    Write-Host "[SKIP] APP_SECRET_KEY is already configured"
}

Write-Host "[RUN] Upgrading pip..."
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

Write-Host "[RUN] Installing runtime and development dependencies..."
& $venvPython -m pip install -r $devRequirements
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install project dependencies."
}

& $venvPython -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "The dependency conflict check failed."
}

Write-Host ""
Write-Host "Project setup completed."
Write-Host "Select .venv\Scripts\python.exe in VS Code, then update the MySQL settings in .env."
