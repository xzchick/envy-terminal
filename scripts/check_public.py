"""Fail on runtime data, obvious secrets, and machine-specific personal paths."""
from pathlib import Path
import re
import subprocess

root=Path(__file__).resolve().parent.parent
try:
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
except subprocess.CalledProcessError:
    tracked=[str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','.venv','__pycache__'))]
patterns=[r'/'+'Users'+r'/[^/\s]+/',r'/'+'home'+r'/[^/\s]+/',r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
errors=[]
for relative in filter(None,tracked):
    p=root/relative
    if p.name in ('accounts.json','account-inventory.json','preferences.json') or p.suffix in ('.gguf','.db','.sqlite3','.log'):
        errors.append(relative+': runtime/private artifact')
    try:text=p.read_text()
    except (UnicodeError,IsADirectoryError):continue
    for pattern in patterns:
        if re.search(pattern,text):errors.append(relative+': possible private data')
if errors:raise SystemExit('\n'.join(errors))
print('Public-package checks passed. Manual review is still required; this is not an exhaustive secret detector.')
