param(
    [switch]$SkipModels,
    [switch]$SkipServe
)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
Push-Location $Repo
try {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
    }
    uv sync --locked --no-editable --python 3.12
    if ($LASTEXITCODE -ne 0) { throw 'uv sync failed.' }
    uv run --locked --no-editable python -c "from envy_terminal.features import private_dir, default_support_dir; private_dir(default_support_dir())"
    if ($LASTEXITCODE -ne 0) { throw 'Failed to initialize private Windows support directory.' }
    if (-not $SkipServe -and $env:ENVY_SKIP_SERVE -ne '1') {
        if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
            throw 'Install Ollama first: https://ollama.com/download/windows'
        }
        & "$PSScriptRoot\start.ps1" -ServeOnly
        if (-not $SkipModels -and $env:ENVY_SKIP_PULL -ne '1') {
            Write-Host 'Downloading the fast model (~5.2 GB), or reusing an existing local copy...'
            $env:OLLAMA_HOST = '127.0.0.1:11435'
            ollama pull qwen3:8b
            if ($LASTEXITCODE -ne 0) { throw 'ollama pull failed.' }
        }
    }
    Write-Host "`nReady. Start with: pwsh -File scripts/start.ps1"
    Write-Host 'Optional Fable install: uv run --no-editable python scripts/install_fable.py'
} finally {
    Pop-Location
}
