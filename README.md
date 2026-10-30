# ENVY Terminal

Local AI. Your Terminal. Sources you can inspect.

A macOS-first assistant for everyday questions, writing, document research, and public-record investigation. Run a fast local model or switch to Fable, search PDFs with page references, and save only the conversations you choose.

![ENVY Terminal overview](hero.svg)

**Terminal only · local model inference · explicit memory · searchable PDFs · public-source research**

## Start here

Download [the complete source project](envy-terminal-source.zip). It includes the Python application, setup scripts, locked dependencies, tests, all guides, and reproducible illustrations. This repository currently distributes the tested project as a source bundle.

Install [Ollama](https://ollama.com/download/mac), [uv](https://docs.astral.sh/uv/getting-started/installation/), and Git. To use a clone of this repository:

```sh
unzip -q envy-terminal-source.zip -d source
cd source/envy-terminal
sh scripts/setup.sh
sh scripts/start.sh
```

Or extract the source ZIP in Finder and open Terminal in its `envy-terminal` folder. Setup downloads the fast model (~5.2 GB); Fable is an optional ~29.8 GB download. Review `docs/SETUP.md` in the bundle before installing Fable:

```sh
uv run --no-editable python scripts/install_fable.py
```

## What you can do

| Task | In Terminal |
|---|---|
| Quick everyday questions | `/fast` |
| Detailed work with installed Fable | `/deep` |
| Save and resume a project | `/chat-save Project` then `/chat-load Project` |
| Remember a preference | `/remember Use short paragraphs` |
| Index a document | `/library-add ` then drag in a PDF |
| Search local evidence | `/library-find proposed launch date` |
| Investigate a public claim | `/check The project has already launched` |
| Research a person in context | `/person Alex Example, project coordinator` |
| Find public court records | `/court case name and jurisdiction` |
| Check citation references | `/audit` |
| Work without web research | `/offline` |

The person above and the supplied example document are fictional. `/person` researches relevant public information, checks identity, and separates facts from allegations; it does not promise access to all information about somebody.

![Terminal example rendered from fictional local source data](terminal-demo.png)

*Illustrative terminal render generated from real library-search code and a fictional fixture. It is not a screenshot of a user's desktop or a claim of completed web research.*

## Included guides

The source bundle contains the complete command guide, installation and hardware guidance, public-person research workflow, assistant instructions, architecture diagram, privacy documentation, troubleshooting history, and validation notes. Look in its `docs/` folder.

## Facts, costs, and boundaries

Local model inference has no provider token bill or daily provider message quota. Tokens still determine context capacity and processing work. Hardware, storage, electricity, website rate limits, and model limitations remain.

Online research contacts search engines and websites. Local inference is not a promise of anonymity. `/offline` disables ENVY's external research tools; it does not disconnect your whole computer.

CourtListener/RECAP offers public records with incomplete coverage. Optional CourtListener tokens are kept in macOS Keychain. PACER is a separate, potentially billable service: this project opens it for manual use and does not automate paid searches or purchases. Saving a PACER password does not create an automated PACER connection.

The models can make mistakes. Fable is a third-party refusal-reduced model, not a guarantee of unlimited capability or perfect accuracy. Citation checks verify that a source reference exists, not that every associated claim is true.

## Develop

```sh
uv sync --locked --no-editable --python 3.12
uv run --no-editable python -m unittest discover -s tests -v
uv run --no-editable python scripts/check_public.py
uv run --no-editable python scripts/render_demo.py
```

Tests run without personal credentials or model downloads. See `CONTRIBUTING.md` inside the bundle for contribution guidance.

MIT for this project's code and documentation. Dependencies and separately downloaded models retain their own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).

---

## Complete command guide

Run `./scripts/start.sh`, then enter commands at `You ›`. Paths containing spaces may be quoted; dragging a file from Finder inserts a usable path. Commands run only when typed by the user, not when requested by a model or a retrieved page.

## Chat and speed

| Command | Meaning |
|---|---|
| `/help` | Show built-in help |
| `/fast` | Select Qwen3 8B by default; remember mode locally |
| `/deep` | Select the separately installed Fable model; remember mode locally |
| `/new` | Start a fresh chat/source ledger; retain preferences and session account connection |
| `/quit`, `/exit`, `/bye` | Exit without automatically saving the conversation |
| Ctrl+C | Interrupt a request and return to the prompt |

Ordinary text is a chat request. The selected model may use research tools when appropriate. Different models have different strengths and refusal behavior. No browser UI is required for chat.

## Saved chats and preferences

| Command | Meaning |
|---|---|
| `/chats` | List named saved chats |
| `/chat-save Name` | Save the conversation and sources locally; confirm before replacing an existing name |
| `/chat-load Name` | Resume a saved chat; confirm before replacing current unsaved messages |
| `/chat-delete Name` | Delete a named saved chat after confirmation |
| `/save /path/export.json` | Export messages and sources to a new file; no overwrite |
| `/remember Preference text` | Persist a non-secret preference and include it in future model prompts |
| `/preferences` | List remembered preferences with numbers |
| `/forget 1` | Delete a numbered preference |
| `/forget all` | Delete all preferences after confirmation |

Names accept letters, digits, spaces, hyphens and underscores. Secrets entered as ordinary messages would become model input and could be saved; use credential commands instead.

## Documents

| Command | Meaning |
|---|---|
| `/file /path/document.pdf` | Attach a document to the conversation; initially extract five PDF pages |
| `/library-add /path/document.pdf` | Index the full PDF/text file for future local keyword searches |
| `/library` | List document IDs, titles, and page/section counts |
| `/library-find search words` | Retrieve matching indexed pages/sections as source IDs |
| `/library-remove DOCUMENT_ID` | Remove an index after confirmation; retain originals and saved chat extracts |
| `/sources` | Show sources retrieved in the current conversation |

Library formats: PDF, TXT, MD, CSV. The full-file index supports files up to 200 MB; web downloads are capped at 50 MB. These are application safeguards, not paid quotas. Split larger files. Scans can take time. Ask the model to retrieve additional page ranges when needed. Indexed text is a snapshot; changed documents need reindexing.

## Research and verification

| Command | Meaning |
|---|---|
| `/search terms` | Search the public web and ask the model to open/cite sources |
| `/read https://example.org/page` | Retrieve a public page/PDF as evidence, then ask a question |
| `/court name and jurisdiction` | Search public CourtListener/RECAP indexes |
| `/person name and identifying context` | Research relevant public information, distinguish namesakes, cite evidence |
| `/check claim` | Ask for an evidence table with support, contradictions, and uncertainties |
| `/audit` | Check source IDs in the last model answer; flag missing IDs and snippet-only citations |
| `/offline` | Disable web search and external document retrieval |
| `/online` | Re-enable external research requests |

Local library search and already attached files remain usable offline. `/audit` does not determine whether a claim is true. See `docs/RESEARCH.md` in the source bundle.

## Accounts

| Command | Meaning |
|---|---|
| `/account-add courtlistener` | Prompt for account name and hidden API token; save the secret to macOS Keychain |
| `/account-use courtlistener` | Activate the saved token for this session |
| `/court-auth` | Enter a token for this session only, without saving it |
| `/account-add pacer` | Save a PACER credential to Keychain; no automatic login or purchases |
| `/accounts` | Show ENVY-stored account names and service websites, never secrets |
| `/account-remove courtlistener` | Remove the selected credential after confirmation; also supports `pacer` |
| `/pacer` | Open the official PACER site manually after the fee notice and confirmation |

The public project has no previous-chat account inventory and does not search other apps' password stores. Credentials and documents must be supplied by each person installing it.

## First local exercise

```text
/offline
/library-add examples/project-juniper.txt
/library-find launch date
What proposed date does the document give, and does it prove the launch happened? Cite the source.
/audit
/chat-save Juniper example
/quit
```

Next session: `/chat-load Juniper example`. The example is fictional and contains conflicting draft/revised dates to exercise evidence handling.
