#!/bin/sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
[ "$(uname -s)" = Darwin ] || { echo 'This setup script targets macOS. See docs/SETUP.md for portability notes.'; exit 1; }
command -v uv >/dev/null || { echo 'Install uv first. See docs/SETUP.md'; exit 1; }
command -v ollama >/dev/null || { echo 'Install Ollama first. See docs/SETUP.md'; exit 1; }
uv sync --locked --no-editable --python 3.12
sh scripts/start.sh --serve-only
if [ "${ENVY_SKIP_PULL:-0}" != 1 ]; then
    echo 'Downloading the fast model (~5.2 GB), or reusing an existing local copy…'
    OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3:8b
fi
if xcrun --find swiftc >/dev/null 2>&1; then
    support="$HOME/Library/Application Support/ENVY Terminal"
    xcrun swiftc -O scripts/envy-ocr.swift -o "$support/envy-ocr"
    echo 'On-device PDF OCR built.'
else
    echo 'OCR skipped: install Xcode Command Line Tools with xcode-select --install, then rerun setup.'
fi
printf '\nReady. Start with: sh scripts/start.sh\nOptional Fable install: uv run --no-editable python scripts/install_fable.py\n'
