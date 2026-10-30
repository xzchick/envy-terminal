# Setup lessons and troubleshooting

This is a generalized record of the problems resolved during development. It intentionally omits personal terminal transcripts, usernames, machine names, accounts, and research subjects.

## “Is a localhost page a website on the internet?”

A browser can display an application served by your own computer. Open WebUI uses that pattern. A browser window does not by itself mean model inference is hosted remotely. This project ultimately uses a Python Terminal interface instead, so Open WebUI is not required.

## Did Open WebUI actually start?

For a separate existing Open WebUI install:

```sh
curl --noproxy '*' --max-time 10 -fsS -w '\nHTTP %{http_code}\n' http://127.0.0.1:8080/ready
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

A `{"status":true}` response with HTTP 200 means that readiness endpoint is responding. It is stronger evidence of startup than an earlier download-progress or warning line. It does not prove every model, embedding feature, or external connection works.

Multiple listeners may indicate duplicate instances or different bind addresses. Inspect each process with `ps -ww -p PID -o pid=,command=` before stopping anything. Do not copy a PID from an old transcript or use broad `killall` commands. A `*:8080` listener is broader than `127.0.0.1:8080`; choose loopback for a local-only service.

Embedding/reranker model downloads can delay document features. A deprecation warning is not automatically fatal. Check the final status and feature-specific errors. This repository does not retain the original private logs and cannot classify every historical warning from them.

## Ollama is unavailable

```sh
sh scripts/start.sh --serve-only
curl --noproxy '*' --max-time 10 -fsS http://127.0.0.1:11435/api/version
curl --noproxy '*' --max-time 10 -fsS http://127.0.0.1:11435/api/tags
```

The normal Ollama desktop service may use port 11434. ENVY's launcher uses 11435 to avoid replacing that service. Read the support-directory log if startup fails. Check the address in `ENVY_OLLAMA_URL` rather than repeatedly starting more servers.

## “Model not found” or a raw GGUF cannot call tools

Run setup for the fast model. For Fable, use `scripts/install_fable.py` and a compatible Ollama version. The original direct registry-name route failed for the chosen filename; downloading a pinned GGUF, checking its checksum, and importing with explicit renderer/parser settings was reproducible. Model names and file names are not interchangeable.

## Slow first answer

The model may be loading into memory. Subsequent requests can reuse it for 30 minutes. `/fast` reduces model size; `/deep` favors the larger Fable model. Search requests, PDF extraction, OCR, long history, and memory pressure add latency. A larger model is not automatically the best everyday setting.

## Missing PDF text

Install Apple's command-line tools and rerun setup to build the OCR helper. OCR can fail or misread a scan. The library reports unreadable pages; do not interpret them as blank evidence. Encrypted, malformed, very large, or unsupported files need manual preparation.

## Website 403, 429, or login page

A 403 is access denied; 429 commonly means rate limiting. Report the failure. Use official manual access or attach a downloaded document. Do not treat a search snippet as proof that the underlying page was read. `/account-use courtlistener` needs a valid token and permitted API access; a PACER password is not a CourtListener API token.

## Tokens and “uncensored” claims

Tokens are text-processing units, not necessarily charges. Local models still have a finite context window. A refusal-reduced model can still refuse, misunderstand, hallucinate, or lack capabilities. Configuration cannot grant access to sealed records, private accounts, or every website.

## Package imports fail in a synced folder

Some macOS file-provider folders mark virtual-environment `.pth` files hidden, and Python can skip them. The supplied commands use `--no-editable` to install a regular wheel instead of depending on editable-import hooks. After changing source, rebuild it with `uv sync --locked --no-editable --reinstall-package envy-terminal`.
