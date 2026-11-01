#!/bin/sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v uv >/dev/null || { echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'; exit 1; }
command -v ollama >/dev/null || { echo 'Install Ollama first: https://ollama.com/download'; exit 1; }
export ENVY_OLLAMA_URL=${ENVY_OLLAMA_URL:-http://127.0.0.1:11435}
# This launcher deliberately supports only its dedicated loopback endpoint.
[ "$ENVY_OLLAMA_URL" = 'http://127.0.0.1:11435' ] || { echo 'For a custom local service, set ENVY_OLLAMA_URL and run uv run envy directly.'; exit 1; }
export OLLAMA_HOST=127.0.0.1:11435
export OLLAMA_NO_CLOUD=1
export OLLAMA_NOHISTORY=1
if [ "$(uname -s)" = Darwin ]; then
    support="$HOME/Library/Application Support/ENVY Terminal"
else
    support="${XDG_DATA_HOME:-$HOME/.local/share}/envy-terminal"
fi
mkdir -p "$support"
chmod 700 "$support"
if ! curl --noproxy '*' --connect-timeout 1 --max-time 2 -fsS "$ENVY_OLLAMA_URL/api/version" >/dev/null 2>&1; then
    echo 'Starting local Ollama on 127.0.0.1:11435…'
    (umask 077; nohup ollama serve >> "$support/ollama.log" 2>&1 < /dev/null &)
    ready=0
    for attempt in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
        if curl --noproxy '*' --max-time 2 -fsS "$ENVY_OLLAMA_URL/api/version" >/dev/null 2>&1; then ready=1; break; fi
        sleep 1
    done
    [ "$ready" = 1 ] || { echo "Ollama did not start. Inspect $support/ollama.log"; exit 1; }
fi
[ "${1:-}" != '--serve-only' ] || exit 0
cd "$repo"
exec uv run --locked --no-editable envy
