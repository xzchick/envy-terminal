import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from envy_terminal import cli, features


class SmokeTests(unittest.TestCase):
    def test_platform_default_support_dirs_and_credential_labels(self):
        with patch.object(features.sys, 'platform', 'darwin'):
            self.assertEqual(features.default_support_dir(), Path.home() / 'Library/Application Support/ENVY Terminal')
            self.assertEqual(features.credential_store_label(), 'macOS Keychain')
        with patch.object(features.sys, 'platform', 'win32'), patch.dict(features.os.environ, {'LOCALAPPDATA': '/tmp/localappdata'}, clear=False):
            self.assertEqual(features.default_support_dir(), Path('/tmp/localappdata') / 'ENVY Terminal')
            self.assertEqual(features.credential_store_label(), 'Windows Credential Manager')
        with patch.object(features.sys, 'platform', 'linux'), patch.dict(features.os.environ, {'XDG_DATA_HOME': '/tmp/xdg'}, clear=False):
            self.assertEqual(features.default_support_dir(), Path('/tmp/xdg') / 'envy-terminal')
            self.assertEqual(features.credential_store_label(), 'OS Secret Service keyring')

    def test_user_path_preserves_windows_backslashes_and_strips_quotes(self):
        win_raw = r'"C:\Users\Example User\Documents\filing.pdf"'
        self.assertEqual(str(cli.user_path(win_raw)), r'C:\Users\Example User\Documents\filing.pdf')
        posix_raw = "'/tmp/example file.txt'"
        self.assertEqual(cli.user_path(posix_raw).as_posix(), '/tmp/example file.txt')

    def test_cli_main_interactive_session_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'data'
            export_file = Path(tmp) / 'exported-session.json'
            doc_file = Path(tmp) / 'notes.txt'
            doc_file.write_text('The contract effective date is October 14.', encoding='utf-8')
            commands = iter([
                '/help',
                '/offline',
                '/remember Cite exact section numbers',
                '/preferences',
                f'/library-add "{doc_file}"',
                '/library',
                '/library-find October 14',
                '/chat-save smoke-session',
                '/chats',
                f'/save "{export_file}"',
                '/audit',
                '/quit',
            ])

            class FakePromptSession:
                def __init__(self, *args, **kwargs):
                    pass

                def prompt(self, message=''):
                    if '[y/N]' in message:
                        return 'y'
                    return next(commands)

            store = features.LocalStore(root)
            orig_research = cli.Research
            try:
                out = io.StringIO()
                with patch.object(cli, 'PromptSession', FakePromptSession), \
                     patch.object(cli, 'warm_model', lambda *a, **k: None), \
                     patch.object(cli, 'Research', side_effect=lambda s=None: orig_research(s or store)), \
                     contextlib.redirect_stdout(out):
                    cli.main()
                self.assertTrue(export_file.is_file())
                exported = json.loads(export_file.read_text(encoding='utf-8'))
                self.assertIn('sources', exported)
                self.assertEqual(store.chats(), ['smoke-session'])
                if os.name == 'nt':
                    sid = features.windows_user_sid()
                    features.verify_windows_sddl(features.windows_sddl(export_file), sid, is_dir=False)
                else:
                    self.assertEqual(export_file.stat().st_mode & 0o777, 0o600)
            finally:
                store.db.close()


if __name__ == '__main__':
    unittest.main()
