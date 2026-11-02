"""Clean-machine installation and launch verification for ENVY Terminal release bundles."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
FORBIDDEN_SUFFIXES = ('.gguf', '.db', '.sqlite3', '.log', '.pot', '.restore')
FORBIDDEN_NAMES = ('accounts.json', 'account-inventory.json', 'preferences.json', '.env')


def verify_checksums(work_dir: Path) -> list[str]:
    sums_file = work_dir / 'SHA256SUMS.txt'
    raw = sums_file.read_bytes()
    if b'\r\n' in raw:
        raise AssertionError('SHA256SUMS.txt must use LF line endings')
    verified = []
    for line in raw.decode('utf-8').splitlines():
        if not line.strip():
            continue
        expected_hash, name = line.split('  ', 1)
        target = work_dir / name
        if not target.is_file():
            raise FileNotFoundError(f'Artifact listed in SHA256SUMS.txt is missing: {name}')
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected_hash:
            raise AssertionError(f'SHA-256 mismatch for {name}: {actual} != {expected_hash}')
        verified.append(name)
    if not verified:
        raise AssertionError('No artifacts found in SHA256SUMS.txt')
    return verified


def main():
    with tempfile.TemporaryDirectory(prefix='envy-clean-machine-') as tmp:
        clean_root = Path(tmp).resolve()
        downloads = clean_root / 'downloads'
        downloads.mkdir(parents=True, exist_ok=True)
        for item in DIST.iterdir():
            if item.is_file():
                shutil.copy2(item, downloads / item.name)

        verified = verify_checksums(downloads)
        print(f"Verified SHA256SUMS.txt for: {', '.join(verified)}")

        is_win = os.name == 'nt'
        archives = list(downloads.glob('envy-terminal-v*.zip' if is_win else 'envy-terminal-v*.tar.gz'))
        if len(archives) != 1:
            raise AssertionError(f'Expected 1 native OS bundle archive, found: {archives}')
        archive = archives[0]

        extract_dir = clean_root / 'extracted'
        extract_dir.mkdir()
        if is_win:
            with zipfile.ZipFile(archive, 'r') as zf:
                zf.extractall(extract_dir)
        else:
            with tarfile.open(archive, 'r:gz') as tf:
                tf.extractall(extract_dir, filter='data')

        bundles = [p for p in extract_dir.iterdir() if p.is_dir()]
        if len(bundles) != 1:
            raise AssertionError(f'Expected 1 top-level bundle directory, found: {bundles}')
        bundle = bundles[0]

        for f in bundle.rglob('*'):
            if f.is_file() and (f.suffix.lower() in FORBIDDEN_SUFFIXES or f.name.lower() in FORBIDDEN_NAMES):
                raise AssertionError(f'Forbidden file found inside release bundle: {f}')

        if sys.platform == 'darwin' and not (bundle / 'bin' / 'envy-ocr').is_file():
            raise AssertionError('Expected prebuilt bin/envy-ocr inside macOS release bundle')

        clean_home = clean_root / 'clean-home'
        clean_home.mkdir()
        env = dict(os.environ)
        env['HOME'] = str(clean_home)
        env['USERPROFILE'] = str(clean_home)
        env['LOCALAPPDATA'] = str(clean_home / 'AppData' / 'Local')
        env['XDG_DATA_HOME'] = str(clean_home / '.local' / 'share')
        env['ENVY_SKIP_SERVE'] = '1'
        env['ENVY_SKIP_PULL'] = '1'
        env.pop('ENVY_DATA_DIR', None)

        if is_win:
            exe = bundle / 'bin' / 'envy' / 'envy.exe'
            subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(bundle / 'setup-envy.ps1'), '-SkipServe', '-SkipModels'],
                cwd=bundle, env=env, check=True,
            )
            bad_env = dict(env, ENVY_OLLAMA_URL='http://192.168.1.99:11435')
            proc = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(bundle / 'start-envy.ps1'), '-ServeOnly'],
                cwd=bundle, env=bad_env, capture_output=True, text=True,
            )
            if proc.returncode == 0 or 'custom local service' not in (proc.stdout + proc.stderr):
                raise AssertionError('Bundled start-envy.ps1 did not reject non-loopback ENVY_OLLAMA_URL')
        else:
            exe = bundle / 'bin' / 'envy' / 'envy'
            subprocess.run(['sh', str(bundle / 'setup-envy.sh')], cwd=bundle, env=env, check=True)
            bad_env = dict(env, ENVY_OLLAMA_URL='http://192.168.1.99:11435')
            proc = subprocess.run(
                ['sh', str(bundle / 'start-envy.sh'), '--serve-only'],
                cwd=bundle, env=bad_env, capture_output=True, text=True,
            )
            if proc.returncode == 0 or 'custom local service' not in (proc.stdout + proc.stderr):
                raise AssertionError('Bundled start-envy.sh did not reject non-loopback ENVY_OLLAMA_URL')

        ver = subprocess.check_output([str(exe), '--version'], cwd=clean_home, env=env, text=True).strip()
        if ver != '0.1.0':
            raise AssertionError(f'Unexpected standalone version output: {ver}')

        export_path = clean_home / 'self-test-export.json'
        self_test_out = subprocess.check_output(
            [str(exe), '--self-test', str(export_path)],
            cwd=clean_home, env=env, text=True,
        )
        payload = json.loads(self_test_out)
        if payload.get('self_test') != 'ok' or not payload.get('locked') or not export_path.is_file():
            raise AssertionError(f'Standalone binary --self-test failed: {self_test_out}')

        print('Clean-machine standalone bundle installation and launch smoke tests passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
