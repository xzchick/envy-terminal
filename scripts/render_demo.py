"""Render a reproducible terminal illustration using fictional, local-only data."""
from pathlib import Path
import io
import tempfile
from rich.console import Console
from rich.terminal_theme import TerminalTheme
from envy_terminal import features

root=Path(__file__).resolve().parent.parent
console=Console(record=True,highlight=False,width=100,file=io.StringIO(),force_terminal=True)
console.print('ENVY AI · Terminal',style='bold cyan')
console.print('Fast local chat · Explicit memory · Sources you can inspect',style='dim')
console.print('\nYou › /offline',style='bold magenta')
console.print('Offline: only the local model and attached sources.')
console.print('\nYou › /library-add examples/project-juniper.txt',style='bold magenta')
with tempfile.TemporaryDirectory() as tmp:
    store=features.LocalStore(Path(tmp)/'data')
    ident,count,blank=store.add_document(root/'examples/project-juniper.txt','/nonexistent-ocr')
    console.print(f'Indexed {count} text section. Fictional example; no personal data.')
    console.print('\nYou › /library-find launch date',style='bold magenta')
    rows=store.search('launch date')
    assert rows
    console.print('[S1] project-juniper.txt · text section 1',style='bold cyan',markup=False)
    # Render the actual indexed fixture without its filesystem-path metadata.
    text=store.db.execute('SELECT text FROM pages WHERE doc=?',(ident,)).fetchone()[0]
    console.print(text.strip(),markup=False)
    store.db.close()
console.print('\nYou › /chat-save Juniper example',style='bold magenta')
console.print('Save this evidence for the next session with an explicit command.',style='dim')
console.print('\nILLUSTRATION · Real indexing output, fictional fixture · No web/model call',style='dim')
theme=TerminalTheme((12,15,26),(223,231,245),[(0,0,0),(255,99,132),(87,214,180),(255,210,100),(110,170,255),(239,113,213),(76,222,235),(223,231,245)])
console.save_svg(str(root/'docs/assets/terminal-demo.svg'),title='ENVY Terminal · fictional local example',theme=theme)
print('Rendered fictional terminal demonstration.')
