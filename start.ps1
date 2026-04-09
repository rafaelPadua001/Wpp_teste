$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (Test-Path .venv) {
    $venvPath = ".venv"
} elseif (Test-Path venv) {
    $venvPath = "venv"
} else {
    python -m venv .venv
    $venvPath = ".venv"
}

& ".\\$venvPath\\Scripts\\Activate.ps1"
pip install -r requirements.txt
if (-not (Test-Path .env) -and (Test-Path .env.example)) { Copy-Item .env.example .env }
uvicorn backend.main:app --reload
