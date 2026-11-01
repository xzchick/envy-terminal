# Install ENVY Terminal

## Requirements

ENVY Terminal supports macOS, Windows, and Linux:

- **macOS**: Uses `~/Library/Application Support/ENVY Terminal`, macOS Keychain, and builds the optional Apple Vision PDF OCR helper (`envy-ocr`) when Xcode Command Line Tools (`xcode-select --install`) are installed.
- **Windows**: Uses `%LOCALAPPDATA%\ENVY Terminal` (protected with owner-only NTFS DACLs), Windows Credential Manager, and PowerShell launchers (`scripts/setup.ps1`, `scripts/start.ps1`).
- **Linux**: Uses `${XDG_DATA_HOME:-~/.local/share}/envy-terminal` (`0700`/`0600`), freedesktop Secret Service keyring, and POSIX shell launchers (`scripts/setup.sh`, `scripts/start.sh`).

Install from the official sources:

- [Ollama](https://ollama.com/download) for macOS, Windows, or Linux
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for managed Python and dependencies
- Git and, on macOS for scanned-PDF OCR, Apple's Command Line Tools: `xcode-select --install`

Open a new Terminal after installing these tools. `command -v ollama`, `command -v uv`, and `git --version` should work. No Homebrew or MacPorts assumption is built into the scripts.

Memory planning is approximate, not a compatibility guarantee. Start with Qwen3 8B on a machine with 16 GB or more unified memory; document context and other apps increase usage. Fable Q8_0 has roughly 30 GB of weights and benefits from substantially more memory—64 GB or more is a practical starting point for this configuration. Check actual memory pressure. Large context, model version, and concurrent apps matter.

## Clone or download

Clone this repository using its GitHub **Code** button, or download and extract the source ZIP. In Terminal, change into the `envy-terminal` folder.

```sh
# macOS and Linux
sh scripts/setup.sh
sh scripts/start.sh
```

```powershell
# Windows PowerShell
pwsh -File scripts/setup.ps1
pwsh -File scripts/start.ps1
```

`setup.sh` creates `.venv` using locked dependencies and Python 3.12. It starts/reuses Ollama at `127.0.0.1:11435`, downloads `qwen3:8b` (~5.2 GB), and builds the OCR helper if the Swift compiler is available. It does not copy chats or credentials from an existing ENVY installation. The public project has a separate `ENVY Terminal` data folder and Keychain namespace.

If Ollama is already running at that address, the script reuses it; make sure it is your intended local-only service. Environment variables in this launcher cannot change a service that was started elsewhere. The launcher starts its own service with `OLLAMA_NO_CLOUD=1` and a loopback-only host. See [Ollama's FAQ](https://docs.ollama.com/faq) for server configuration.

For development against an already downloaded model, `ENVY_SKIP_PULL=1 sh scripts/setup.sh` skips the pull. If you use that option without the model installed, chat will report a missing model.

## Add Fable

First read the [publisher's model card](https://huggingface.co/DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored-NM-DAU-NEO-MTP-GGUF), including upstream licensing and model limitations.

```sh
sh scripts/start.sh --serve-only
uv run --no-editable python scripts/install_fable.py
```

The installer asks before downloading. It pins a model revision, checks SHA-256, then imports it as `envy-fable`. The download is about 29.8 GB. Allow roughly 65 GB free because the Hugging Face cache and Ollama may both retain a copy. A cached verified file can be reused. No Hugging Face token is required or implicitly sent by this helper.

The import template includes `RENDERER qwen3.5` and `PARSER qwen3.5`, which the tested Ollama version needed for structured chat/tools. If your Ollama rejects those directives or does not support this model family, update Ollama from its official source. A successful download alone is not proof of working tool calls.

In ENVY:

```text
/deep
```

Return to `/fast` for smaller, faster inference. A model switch can incur a load delay. Neither mode promises zero refusals or unlimited context.

## Launch and configure

Run `sh scripts/start.sh` from the repository. For a custom existing local Ollama endpoint:

```sh
export ENVY_OLLAMA_URL=http://127.0.0.1:11434
uv run --locked --no-editable envy
```

The Python client rejects non-loopback model endpoints. Optional variables are documented in `.env.example`; that file is not loaded automatically. Model overrides are `ENVY_FAST_MODEL` and `ENVY_DEEP_MODEL`. Visible mode labels describe the default models.

## Updates and removal

Pull reviewed updates, then run `uv sync --locked --no-editable`. Keep private data outside Git. To stop a chat, use `/quit`; Ollama stays available and unloads idle models after the configured keep-alive period. Do not kill every Python or Ollama process just to stop ENVY.

To remove the project, remove its checkout and `.venv`. Separately review the `ENVY Terminal` support directory, explicitly saved exports, and ENVY Keychain entries. Use `/account-remove` before deleting the environment if you want the app to remove its own credentials. Model removal is a separate deliberate Ollama action; other apps may share those models.
