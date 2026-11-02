"""Build standalone native OS release bundles, Python wheel/sdist, and SHA256SUMS.txt for ENVY Terminal."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
BUILD = ROOT / 'build'
VERSION = '0.1.0'
FORBIDDEN_SUFFIXES = ('.gguf', '.db', '.sqlite3', '.log', '.pot', '.restore')
FORBIDDEN_NAMES = ('accounts.json', 'account-inventory.json', 'preferences.json', '.env')


def platform_tag():
    if sys.platform == 'darwin':
        os_name = 'macos'
    elif os.name == 'nt':
        os_name = 'windows'
    elif sys.platform.startswith('linux'):
        os_name = 'linux'
    else:
        os_name = sys.platform
    machine = platform.machine().lower()
    if machine in ('amd64', 'x86_64', 'x64'):
        arch = 'x86_64'
    elif machine in ('arm64', 'aarch64'):
        arch = 'arm64'
    else:
        arch = machine or 'unknown'
    return os_name, arch


def write_standalone_launchers(bundle_dir: Path, is_win: bool):
    if is_win:
        setup_ps1 = bundle_dir / 'setup-envy.ps1'
        setup_ps1.write_text(
            "param(\n"
            "    [switch]$SkipModels,\n"
            "    [switch]$SkipServe\n"
            ")\n"
            "$ErrorActionPreference = 'Stop'\n"
            "$Exe = Join-Path $PSScriptRoot 'bin\\envy\\envy.exe'\n"
            "if (-not (Test-Path $Exe)) { throw \"Standalone executable missing: $Exe\" }\n"
            "& $Exe --init-support-dir | Out-Null\n"
            "if ($LASTEXITCODE -ne 0) { throw 'Failed to initialize private Windows support directory.' }\n"
            "if (-not $SkipServe -and $env:ENVY_SKIP_SERVE -ne '1') {\n"
            "    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {\n"
            "        throw 'Install Ollama first: https://ollama.com/download/windows'\n"
            "    }\n"
            "    & (Join-Path $PSScriptRoot 'start-envy.ps1') -ServeOnly\n"
            "    if (-not $SkipModels -and $env:ENVY_SKIP_PULL -ne '1') {\n"
            "        Write-Host 'Downloading the fast model (~5.2 GB), or reusing an existing local copy...'\n"
            "        $env:OLLAMA_HOST = '127.0.0.1:11435'\n"
            "        ollama pull qwen3:8b\n"
            "        if ($LASTEXITCODE -ne 0) { throw 'ollama pull failed.' }\n"
            "    }\n"
            "}\n"
            "Write-Host \"`nReady. Start with: powershell -ExecutionPolicy Bypass -File .\\start-envy.ps1\"\n",
            encoding='utf-8',
        )
        start_ps1 = bundle_dir / 'start-envy.ps1'
        start_ps1.write_text(
            "param(\n"
            "    [switch]$ServeOnly\n"
            ")\n"
            "$ErrorActionPreference = 'Stop'\n"
            "if (-not $env:ENVY_OLLAMA_URL) { $env:ENVY_OLLAMA_URL = 'http://127.0.0.1:11435' }\n"
            "if ($env:ENVY_OLLAMA_URL -ne 'http://127.0.0.1:11435') {\n"
            "    throw 'For a custom local service, set ENVY_OLLAMA_URL and run bin\\envy\\envy.exe directly.'\n"
            "}\n"
            "if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {\n"
            "    throw 'Install Ollama first: https://ollama.com/download/windows'\n"
            "}\n"
            "$env:OLLAMA_HOST = '127.0.0.1:11435'\n"
            "$env:OLLAMA_NO_CLOUD = '1'\n"
            "$env:OLLAMA_NOHISTORY = '1'\n"
            "function Test-LocalOllama {\n"
            "    try {\n"
            "        $req = [System.Net.WebRequest]::Create(\"$env:ENVY_OLLAMA_URL/api/version\")\n"
            "        $req.Proxy = $null; $req.Timeout = 2000\n"
            "        $resp = $req.GetResponse(); $resp.Close(); return $true\n"
            "    } catch { return $false }\n"
            "}\n"
            "$Exe = Join-Path $PSScriptRoot 'bin\\envy\\envy.exe'\n"
            "& $Exe --init-support-dir | Out-Null\n"
            "if ($LASTEXITCODE -ne 0) { throw 'Failed to lock support directory.' }\n"
            "$SupportBase = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME 'AppData\\Local' }\n"
            "$Support = Join-Path $SupportBase 'ENVY Terminal'\n"
            "if (-not (Test-LocalOllama)) {\n"
            "    Write-Host 'Starting local Ollama on 127.0.0.1:11435...'\n"
            "    $LogFile = Join-Path $Support 'ollama.log'\n"
            "    Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError \"$LogFile.err\"\n"
            "    $Ready = $false\n"
            "    for ($i = 0; $i -lt 20; $i++) {\n"
            "        if (Test-LocalOllama) { $Ready = $true; break }\n"
            "        Start-Sleep -Seconds 1\n"
            "    }\n"
            "    if (-not $Ready) { throw \"Ollama did not start. Inspect $LogFile\" }\n"
            "}\n"
            "if ($ServeOnly) { return }\n"
            "& $Exe\n"
            "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n",
            encoding='utf-8',
        )
    else:
        setup_sh = bundle_dir / 'setup-envy.sh'
        setup_sh.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "bundle=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)\n"
            "exe=\"$bundle/bin/envy/envy\"\n"
            "[ -x \"$exe\" ] || { echo \"Standalone executable missing: $exe\" >&2; exit 1; }\n"
            "support=$(\"$exe\" --init-support-dir)\n"
            "if [ -f \"$bundle/bin/envy-ocr\" ]; then\n"
            "    [ ! -L \"$support/envy-ocr\" ] || { echo 'Refusing symlinked envy-ocr target' >&2; exit 1; }\n"
            "    rm -f \"$support/envy-ocr\"\n"
            "    cp \"$bundle/bin/envy-ocr\" \"$support/envy-ocr\"\n"
            "    chmod 700 \"$support/envy-ocr\"\n"
            "fi\n"
            "if [ \"${ENVY_SKIP_SERVE:-0}\" != 1 ]; then\n"
            "    command -v ollama >/dev/null || { echo 'Install Ollama first: https://ollama.com/download'; exit 1; }\n"
            "    sh \"$bundle/start-envy.sh\" --serve-only\n"
            "    if [ \"${ENVY_SKIP_PULL:-0}\" != 1 ]; then\n"
            "        echo 'Downloading the fast model (~5.2 GB), or reusing an existing local copy…'\n"
            "        OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3:8b\n"
            "    fi\n"
            "fi\n"
            "printf '\\nReady. Start with: sh ./start-envy.sh\\n'\n",
            encoding='utf-8',
        )
        setup_sh.chmod(0o755)
        start_sh = bundle_dir / 'start-envy.sh'
        start_sh.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "bundle=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)\n"
            "exe=\"$bundle/bin/envy/envy\"\n"
            "export ENVY_OLLAMA_URL=${ENVY_OLLAMA_URL:-http://127.0.0.1:11435}\n"
            "[ \"$ENVY_OLLAMA_URL\" = 'http://127.0.0.1:11435' ] || { echo 'For a custom local service, set ENVY_OLLAMA_URL and run bin/envy/envy directly.'; exit 1; }\n"
            "command -v ollama >/dev/null || { echo 'Install Ollama first: https://ollama.com/download'; exit 1; }\n"
            "command -v curl >/dev/null || { echo 'Install curl first.'; exit 1; }\n"
            "export OLLAMA_HOST=127.0.0.1:11435\n"
            "export OLLAMA_NO_CLOUD=1\n"
            "export OLLAMA_NOHISTORY=1\n"
            "support=$(\"$exe\" --init-support-dir)\n"
            "if ! curl --noproxy '*' --connect-timeout 1 --max-time 2 -fsS \"$ENVY_OLLAMA_URL/api/version\" >/dev/null 2>&1; then\n"
            "    echo 'Starting local Ollama on 127.0.0.1:11435…'\n"
            "    (umask 077; nohup ollama serve >> \"$support/ollama.log\" 2>&1 < /dev/null &)\n"
            "    ready=0\n"
            "    for attempt in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do\n"
            "        if curl --noproxy '*' --max-time 2 -fsS \"$ENVY_OLLAMA_URL/api/version\" >/dev/null 2>&1; then ready=1; break; fi\n"
            "        sleep 1\n"
            "    done\n"
            "    [ \"$ready\" = 1 ] || { echo \"Ollama did not start. Inspect $support/ollama.log\"; exit 1; }\n"
            "fi\n"
            "[ \"${1:-}\" != '--serve-only' ] || exit 0\n"
            "exec \"$exe\"\n",
            encoding='utf-8',
        )
        start_sh.chmod(0o755)


def main():
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'check_public.py')], cwd=ROOT, check=True)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    # 1. Build universal Python wheel and sdist (preserved alongside standalone bundles)
    subprocess.run(['uv', 'build', '--wheel', '--sdist', '--out-dir', str(DIST)], cwd=ROOT, check=True)

    # 2. Build standalone native OS application folder via PyInstaller
    pyi_dist = BUILD / 'pyi-dist'
    pyi_work = BUILD / 'pyi-work'
    pyi_spec = BUILD / 'pyi-spec'
    for d in (pyi_dist, pyi_work, pyi_spec):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    pyi_entry = pyi_spec / 'envy_entry.py'
    pyi_entry.write_text(
        "from envy_terminal.cli import main\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n",
        encoding='utf-8',
    )

    subprocess.run(
        [
            'uv', 'run', '--with', 'pyinstaller',
            'pyinstaller', '--noconfirm', '--clean', '--onedir',
            '--name', 'envy',
            '--paths', str(ROOT / 'src'),
            '--collect-submodules', 'keyring.backends',
            '--distpath', str(pyi_dist),
            '--workpath', str(pyi_work),
            '--specpath', str(pyi_spec),
            str(pyi_entry),
        ],
        cwd=ROOT,
        check=True,
    )

    os_name, arch = platform_tag()
    is_win = os.name == 'nt'
    bundle_name = f'envy-terminal-v{VERSION}-{os_name}-{arch}'
    staging_root = BUILD / 'release-staging'
    if staging_root.exists():
        shutil.rmtree(staging_root)
    bundle_dir = staging_root / bundle_name
    (bundle_dir / 'bin').mkdir(parents=True, exist_ok=True)

    shutil.copytree(pyi_dist / 'envy', bundle_dir / 'bin' / 'envy')

    # On macOS, compile Apple Vision OCR helper into the bundle if swiftc is present
    if sys.platform == 'darwin' and shutil.which('xcrun'):
        rc = subprocess.run(['xcrun', '--find', 'swiftc'], capture_output=True).returncode
        if rc == 0:
            ocr_out = bundle_dir / 'bin' / 'envy-ocr'
            subprocess.run(['xcrun', 'swiftc', '-O', str(ROOT / 'scripts' / 'envy-ocr.swift'), '-o', str(ocr_out)], cwd=ROOT, check=True)
            ocr_out.chmod(0o755)

    write_standalone_launchers(bundle_dir, is_win)
    (bundle_dir / 'docs').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'docs' / 'SETUP.md', bundle_dir / 'docs' / 'SETUP.md')
    for doc in ('README.md', 'RELEASE_NOTES.md', 'LICENSE'):
        src = ROOT / doc
        if src.is_file():
            shutil.copy2(src, bundle_dir / doc)

    # Scan bundle for any forbidden private/model files (case-insensitive)
    for item in bundle_dir.rglob('*'):
        if item.is_file():
            low_name = item.name.lower()
            low_suffix = item.suffix.lower()
            if low_suffix in FORBIDDEN_SUFFIXES or low_name in FORBIDDEN_NAMES or low_name.startswith('.env'):
                raise RuntimeError(f'Forbidden file in release bundle: {item}')

    def clean_tarinfo(ti: tarfile.TarInfo) -> tarfile.TarInfo:
        ti.uid = 0
        ti.gid = 0
        ti.uname = 'root'
        ti.gname = 'root'
        return ti

    if is_win:
        archive_path = DIST / f'{bundle_name}.zip'
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(bundle_dir.rglob('*')):
                if item.is_file():
                    zf.write(item, item.relative_to(staging_root))
    else:
        archive_path = DIST / f'{bundle_name}.tar.gz'
        with tarfile.open(archive_path, 'w:gz') as tf:
            tf.add(bundle_dir, arcname=bundle_name, filter=clean_tarinfo)

    lines = []
    for artifact in sorted(DIST.iterdir()):
        if artifact.is_file() and artifact.name != 'SHA256SUMS.txt':
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            lines.append(f'{digest}  {artifact.name}')
    sums_path = DIST / 'SHA256SUMS.txt'
    sums_path.write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    print(sums_path.read_text(encoding='utf-8'), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
