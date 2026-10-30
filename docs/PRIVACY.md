# Privacy and credentials

The repository contains program code, synthetic fixtures, diagrams, and generic instructions. It contains no user chats, account inventory, real case files, passwords, cookies, or API tokens. The public version does not read previous ChatGPT conversations or discover your accounts. Add your own preferences and documents only after installing it.

| Data | Where it goes |
|---|---|
| Model prompt and answer | Local Ollama endpoint |
| Web search keywords | External search providers, only in online mode |
| Requested public URL | The requested website and any permitted redirects |
| Indexed files and OCR text | Local SQLite index |
| Saved chats/preferences | Local JSON files |
| Credential secret entered through `/account-add` | macOS Keychain |
| Account name and service website | Local account metadata |
| CourtListener token, when activated | CourtListener's API for requested records |

Default storage: `~/Library/Application Support/ENVY Terminal/data/`. Directories are mode 700 and app-created JSON/index files are mode 600. These local files are not separately encrypted by ENVY. Your OS, backups, exports, and Terminal state can retain data. Deletion here does not guarantee removal from backups.

Use `/offline` to disable ENVY web tools. This setting does not disable the Mac's networking, other programs, or a separate model server's cloud configuration. The included launcher sets local-only options for a server it starts. A pre-existing server must be configured separately.

## Enter credentials privately

```text
/account-add courtlistener
/account-use courtlistener
```

Enter a service account name, then the token in the hidden prompt. The token is never included in model messages, the source ledger, or chat exports. `/court-auth` provides session-only entry instead.

```text
/account-add pacer
```

This stores a password but does not log into PACER automatically. `/pacer` remains manual. The credential backend is explicitly macOS Keychain; there is no plaintext fallback. Keychain access may require an OS prompt. Other software running as your user may have access according to your Keychain settings; this is not a separate password-manager security boundary.

`/accounts` displays saved account names and websites, never secrets. `/account-remove <service>` deletes ENVY's selected Keychain credential. Never type secrets into ordinary chat or preferences: those channels are model input and may be explicitly saved. The preference keyword check is only a convenience, not a comprehensive secret detector.

## Publishing your fork

Never commit runtime data, model weights, logs, exports, `.env` files, or screenshots of real account screens. Run the public-package check and inspect `git diff --cached`. Review Git commit author/committer email too; `.gitignore` does not hide commit metadata. Use GitHub's no-reply email if publishing under a personal account. The included visuals use fictional data and are reproducible.
