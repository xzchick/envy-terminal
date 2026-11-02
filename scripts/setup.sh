#!/bin/sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
os_name=$(uname -s)
case "$os_name" in
    Darwin|Linux) ;;
    *) echo 'For Windows, run: powershell -File scripts\setup.ps1'; exit 1 ;;
esac
command -v uv >/dev/null || { echo 'Install uv first. See docs/SETUP.md'; exit 1; }
uv sync --locked --no-editable --python 3.12
uv run --locked --no-editable python -c "from envy_terminal.features import private_dir, default_support_dir; private_dir(default_support_dir())"
if [ "${ENVY_SKIP_SERVE:-0}" != 1 ]; then
    command -v ollama >/dev/null || { echo 'Install Ollama first. See docs/SETUP.md'; exit 1; }
    sh scripts/start.sh --serve-only
    if [ "${ENVY_SKIP_PULL:-0}" != 1 ]; then
        echo 'Downloading the fast model (~5.2 GB), or reusing an existing local copy…'
        OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3:8b
    fi
fi
if [ "$os_name" = Darwin ]; then
    if xcrun --find swiftc >/dev/null 2>&1; then
        support="$HOME/Library/Application Support/ENVY Terminal"
        if [ -L "$support" ]; then
            echo "Refusing symlinked support directory: $support" >&2
            exit 1
        fi
        mkdir -p -m 700 "$support"
        chmod 700 "$support"
        xcrun swiftc -O scripts/envy-ocr.swift -o "$support/envy-ocr"
        echo 'On-device PDF OCR built.'
    else
        echo 'OCR skipped: install Xcode Command Line Tools with xcode-select --install, then rerun setup.'
    fi
else
    echo 'Linux environment ready (Swift Vision OCR helper is macOS-only; text PDFs and all other features are enabled).'
fi
printf '\nReady. Start with: sh scripts/start.sh\nOptional Fable install: uv run --no-editable python scripts/install_fable.py\n'
