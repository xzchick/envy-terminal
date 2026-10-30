# Validation and limits

Release preparation checked:

- Clean Python 3.12 environment created from the locked dependency set.
- Regular-wheel installation and Terminal launcher startup on Apple Silicon macOS.
- Native Swift OCR helper compiled successfully.
- Eleven automated tests covering save/load/delete, private file permissions, path-name validation, preference changes, Keychain metadata isolation (mocked backend), offline library retrieval, bounded page ranges, citation auditing, private-address rejection, embedded-credential rejection, and the PACER separation.
- Live fast-model test: searched the fictional Project Juniper document offline and returned the proposed date with a source reference, distinguishing a proposal from proof of occurrence.
- Public-package scan and manual review of staged files, including exclusion of runtime data and machine-specific paths.
- Visual review of the synthetic terminal illustration, hero, and architecture diagram.

The public package builds on a locally tested Fable import and research client. The large Fable file was not downloaded again solely for this release. The helper pins the previously verified revision and checksum; future upstream availability and runtime compatibility may change.

No real account credentials are fixtures. The release tests do not log into PACER or CourtListener, perform paid queries, or verify a specific person's account. The Keychain backend is available on the test platform; credential isolation is covered with a mocked backend rather than a published secret.

CI runs the offline unit tests and public-package checker. It does not download large models, access real accounts, test live search-provider availability, or certify factual accuracy.

Known limitations:

- macOS-first setup, OCR, and credentials; no Windows/Linux compatibility promise.
- Keyword search can miss semantically related text; no embedding model is included.
- OCR and model answers may be wrong; inspect original pages.
- Character-based history trimming is approximate, not unlimited context.
- Site restrictions, API quotas, and missing public records remain.
- Local chat/index files are not separately encrypted by the app.
- No automatic account discovery, PACER login, paid record retrieval, background monitoring, or remote cloud model inference is implemented.
- Web-fetch controls are intended for a personal local app, not hostile multi-user deployment.

To rerun after editing source:

```sh
uv sync --locked --no-editable --reinstall-package envy-terminal
uv run --no-editable python -m unittest discover -s tests -v
uv run --no-editable python scripts/check_public.py
```
