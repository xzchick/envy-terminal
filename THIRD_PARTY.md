# Third-party components

This project's MIT license covers its own source and documentation, not downloaded model weights or third-party dependencies.

- [Ollama](https://github.com/ollama/ollama): local model runtime, installed separately.
- [Qwen3 8B](https://ollama.com/library/qwen3:8b): default fast model; consult its upstream license/model card.
- [DavidAU Fable model](https://huggingface.co/DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored-NM-DAU-NEO-MTP-GGUF): optional third-party model. The publisher labels the repository Apache-2.0; review upstream components and current terms. The project provides download/import instructions, not model weights.
- [uv](https://github.com/astral-sh/uv): environment and lockfile management.
- Python packages in `pyproject.toml` / `uv.lock`: HTTPX, Beautiful Soup, pypdf, DDGS, Rich, prompt-toolkit, keyring, Hugging Face Hub, and their dependencies. Their upstream licenses apply.
- Apple PDFKit/Vision/AppKit: used by the optional native OCR helper under the applicable Apple platform terms.

Public web providers, CourtListener, and PACER have independent access rules, fees where applicable, and usage limits. The project does not grant service rights or redistribute records.
