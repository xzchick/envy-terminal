# ENVY Terminal v0.1.0 Release Notes (Draft / Non-Production)

## Overview
ENVY Terminal is a local-first research, document analysis, and citation-auditing assistant for **macOS, Windows, and Linux**. It runs against a dedicated local loopback Ollama server (`127.0.0.1:11435`, `OLLAMA_NO_CLOUD=1`) and stores credentials exclusively in native OS credential stores (macOS Keychain, Windows Credential Manager, or Linux Secret Service).

## Release Artifacts

Each GitHub Release provides two distinct distribution tiers:

1. **Standalone Native OS Bundles (No Python or `uv` Required):**
   - `envy-terminal-v0.1.0-macos-arm64.tar.gz` — Standalone `bin/envy/envy` binary, prebuilt `bin/envy-ocr` Apple Vision PDF OCR helper, and `setup-envy.sh` / `start-envy.sh` launchers
   - `envy-terminal-v0.1.0-windows-x86_64.zip` — Standalone `bin\envy\envy.exe` binary and `setup-envy.ps1` / `start-envy.ps1` PowerShell launchers
   - `envy-terminal-v0.1.0-linux-x86_64.tar.gz` — Standalone `bin/envy/envy` binary and `setup-envy.sh` / `start-envy.sh` launchers
2. **Universal Python Packages (For Existing Python 3.12+ / `uv` / `pip` Environments):**
   - `envy_terminal-0.1.0-py3-none-any.whl` — Pure-Python wheel (not a standalone OS installer)
   - `envy_terminal-0.1.0.tar.gz` — Source distribution
3. **Checksums:**
   - `SHA256SUMS.txt` — LF-normalized SHA-256 checksums for every archive, wheel, and sdist above

> **Privacy & Model Policy:** No Ollama model weights (`.gguf`), private databases, chat histories, or credentials are bundled in any release artifact. Install [Ollama](https://ollama.com/download) separately; the setup launcher pulls `qwen3:8b` locally when you run setup.

## Verify Checksums Before Installing

### macOS and Linux
```sh
shasum -a 256 --ignore-missing -c SHA256SUMS.txt
```
*(Note: On macOS, if Gatekeeper quarantines an unsigned downloaded archive, verify the SHA-256 digest above first, then run `xattr -dr com.apple.quarantine envy-terminal-v0.1.0-macos-*`.)*

### Windows PowerShell
```powershell
$expected = (Select-String -Path .\SHA256SUMS.txt -Pattern 'envy-terminal-v0.1.0-windows-x86_64.zip').Line.Split(' ')[0]
$actual = (Get-FileHash .\envy-terminal-v0.1.0-windows-x86_64.zip -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw "SHA-256 mismatch: $actual != $expected" } else { "SHA-256 verified: $actual" }
```

## Quick Start (Standalone Bundle)

### macOS and Linux
```sh
tar -xzf envy-terminal-v0.1.0-<os>-<arch>.tar.gz
cd envy-terminal-v0.1.0-<os>-<arch>
sh ./setup-envy.sh
sh ./start-envy.sh
```

### Windows PowerShell
```powershell
Expand-Archive .\envy-terminal-v0.1.0-windows-x86_64.zip -DestinationPath .
cd .\envy-terminal-v0.1.0-windows-x86_64
powershell -ExecutionPolicy Bypass -File .\setup-envy.ps1
powershell -ExecutionPolicy Bypass -File .\start-envy.ps1
```
