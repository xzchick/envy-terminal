# Complete command guide

Run `sh scripts/start.sh`, then enter commands at `You ›`. Paths containing spaces may be quoted; dragging a file from Finder inserts a usable path. Commands run only when typed by the user, not when requested by a model or a retrieved page.

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

Local library search and already attached files remain usable offline. `/audit` does not determine whether a claim is true. See [RESEARCH.md](RESEARCH.md).

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
