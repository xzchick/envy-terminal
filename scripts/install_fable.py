"""Download a pinned third-party GGUF, verify SHA-256, then import locally."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
from huggingface_hub import hf_hub_download

REPO='DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored-NM-DAU-NEO-MTP-GGUF'
REVISION='7dafa1583bef3c77dd3b72262a207cfad39d377f'
FILENAME='Qwen3.8-27B-TTURBO-Fable-C-Fusion-709-U-Httic-Uncen-NM-DAU-NEO-MAX-Q8_0.gguf'
SHA256='cb6d30dfbdecd6cc76d10bb1b15c87ee6cceaaf31a34c0d650983ad4bf73194c'

def main():
    if not shutil.which('ollama'):raise SystemExit('Install Ollama first.')
    print('Downloads ~29.8 GB. Allow ~65 GB free for the download and Ollama import.')
    print('Read the model card and upstream licensing before use; weights are not part of this project.')
    print('https://huggingface.co/'+REPO)
    if input('Download, verify, and create/update the envy-fable model? [y/N] ').lower()!='y':return
    path=Path(hf_hub_download(REPO,FILENAME,revision=REVISION,token=False))
    digest=hashlib.sha256()
    with path.open('rb') as f:
        while chunk:=f.read(8*1024*1024):digest.update(chunk)
    if digest.hexdigest()!=SHA256:raise SystemExit('Checksum mismatch. Model was not imported.')
    template=(Path(__file__).parent.parent/'models/Fable.Modelfile.in').read_text()
    # Ollama accepts a quoted absolute FROM path. Reject unusual filename delimiters.
    if any(c in str(path) for c in ('"','\n','\r')):raise SystemExit('Unsupported download path.')
    with tempfile.TemporaryDirectory(prefix='envy-model-') as tmp:
        modelfile=Path(tmp)/'Modelfile';modelfile.write_text(template.replace('@GGUF_PATH@',str(path)))
        env=dict(os.environ,OLLAMA_HOST='127.0.0.1:11435',OLLAMA_NO_CLOUD='1')
        subprocess.run(['ollama','create','envy-fable','-f',str(modelfile)],env=env,check=True)
    print('Fable installed. Start ENVY and enter /deep.')

if __name__=='__main__':main()
