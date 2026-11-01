param(
    [switch]$ServeOnly
)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw 'Install Ollama first: https://ollama.com/download/windows'
}
if (-not $env:ENVY_OLLAMA_URL) {
    $env:ENVY_OLLAMA_URL = 'http://127.0.0.1:11435'
}
if ($env:ENVY_OLLAMA_URL -ne 'http://127.0.0.1:11435') {
    throw 'For a custom local service, set ENVY_OLLAMA_URL and run uv run envy directly.'
}
$env:OLLAMA_HOST = '127.0.0.1:11435'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_NOHISTORY = '1'

Push-Location $Repo
try {
    $Support = (uv run --no-editable python -c "from envy_terminal.features import private_dir, default_support_dir; print(private_dir(default_support_dir()))").Trim()
    if ($LASTEXITCODE -ne 0 -or -not $Support) { throw 'Failed to lock support directory.' }
    $Ready = $false
    try {
        $null = Invoke-RestMethod -Uri "$env:ENVY_OLLAMA_URL/api/version" -TimeoutSec 2 -NoProxy
        $Ready = $true
    } catch {}
    if (-not $Ready) {
        Write-Host 'Starting local Ollama on 127.0.0.1:11435...'
        $LogFile = Join-Path $Support 'ollama.log'
        Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError "$LogFile.err"
        for ($i = 0; $i -lt 20; $i++) {
            try {
                $null = Invoke-RestMethod -Uri "$env:ENVY_OLLAMA_URL/api/version" -TimeoutSec 2 -NoProxy
                $Ready = $true
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        if (-not $Ready) {
            throw "Ollama did not start. Inspect $LogFile"
        }
    }
    if ($ServeOnly) { return }
    uv run --locked --no-editable envy
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
