import tempfile,unittest,json,io,contextlib,os
from pathlib import Path
from unittest.mock import patch
from envy_terminal import features as f
from envy_terminal import cli as e
class FeaturesTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.store=f.LocalStore(self.root/'data');self.app=e.Research(self.store)
 def tearDown(self):self.store.db.close();self.temp.cleanup()
 def test_session_roundtrip_excludes_credentials(self):
  self.app.court_token='secret-token-never-persist';self.app.messages.append({'role':'user','content':'hello'});self.app.allowed_files.add('/a/file.pdf');self.app.online=False;self.app.mode='fast'
  self.store.save('example',self.app);raw=(self.store.sessions/'example.json').read_text(encoding='utf-8');self.assertNotIn('secret-token',raw)
  other=e.Research(self.store);self.store.load('example',other);self.assertEqual(other.messages[-1]['content'],'hello');self.assertFalse(other.online);self.assertEqual(other.mode,'fast');self.assertEqual(other.allowed_files,{'/a/file.pdf'});self.assertIsNone(other.court_token)
  self.store.delete_chat('example');self.assertEqual(self.store.chats(),[])
 def test_private_storage_and_traversal(self):
  for bad in ('../../escape','CON','nul','com1','',' leading','a'*81):
   with self.assertRaises(ValueError):self.store.save(bad,self.app)
  self.store.save('safe',self.app);self.store.configure()
  safe=self.store.sessions/'safe.json';db=self.store.root/'library.sqlite3';cfg=self.store.config
  if os.name=='nt':
   sid=f.windows_user_sid()
   self.assertEqual(f.resolve_windows_sid('WD'),'S-1-1-0')
   self.assertEqual(f.resolve_windows_sid('BA'),'S-1-5-32-544')
   self.assertEqual(f.resolve_windows_sid('SY'),'S-1-5-18')
   la_sid=f.resolve_windows_sid('LA')
   self.assertTrue(la_sid.startswith('S-1-5-21-') and la_sid.endswith('-500'))
   for d in (self.store.root,self.store.sessions):
    f.verify_windows_sddl(f.windows_sddl(d),sid,is_dir=True)
   for file_path in (safe,db,cfg):
    f.verify_windows_sddl(f.windows_sddl(file_path),sid,is_dir=False)
  else:
   for d in (self.store.root,self.store.sessions):
    self.assertEqual(d.stat().st_mode&0o777,0o700)
   for file_path in (safe,db,cfg):
    self.assertEqual(file_path.stat().st_mode&0o777,0o600)
  sid='S-1-5-21-1000-2000-3000-1001'
  local_admin='S-1-5-21-1000-2000-3000-500'
  other_domain_admin='S-1-5-21-9999-8888-7777-500'
  fake_map={'SY':'S-1-5-18','BA':'S-1-5-32-544','LA':local_admin,'WD':'S-1-1-0','BU':'S-1-5-32-545'}
  def fake_resolve(t):
   u=t.strip().upper()
   if u.startswith('S-1-'):return u
   if u in fake_map:return fake_map[u]
   raise PermissionError(u)
  with patch.object(f,'resolve_windows_sid',side_effect=fake_resolve):
   f.verify_windows_sddl(f'O:{sid}D:PAI(A;OICI;FA;;;{sid})(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)',sid,is_dir=True)
   f.verify_windows_sddl(f'O:BAD:PAI(A;;FA;;;{sid})(A;;FA;;;SY)(A;;FA;;;BA)',sid,is_dir=False)
   f.verify_windows_sddl('O:LAD:PAI(A;OICI;FA;;;LA)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)',local_admin,is_dir=True)
   for insecure in (
    f'D:P(A;OICI;FA;;;{sid})',
    f'O:{sid}D:AI(A;OICI;FA;;;{sid})',
    f'O:{sid}D:P(A;OICIID;FA;;;{sid})',
    f'O:{sid}D:P(A;OICIIO;FA;;;{sid})',
    f'O:{sid}D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;S-1-1-0)',
    f'O:{sid}D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;S-1-5-32-545)',
    f'O:{sid}D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;WD)',
    f'O:{sid}D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;BU)',
    f'O:{sid}D:P(A;OICI;FA;;;{sid})(A;OICI;FA;;;LA)',
    f'O:{other_domain_admin}D:P(A;OICI;FA;;;{sid})',
    f'O:{sid}D:P(A;OICI;FA;;;SY)',
   ):
    with self.assertRaises(PermissionError):f.verify_windows_sddl(insecure,sid,is_dir=True)
   with self.assertRaises(PermissionError):
    f.verify_windows_sddl('O:LAD:PAI(A;OICI;FA;;;LA)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)',other_domain_admin,is_dir=True)
 def test_library_offline_and_delete(self):
  p=self.root/'evidence.txt';p.write_text('The hearing was postponed to September. A complaint is an allegation.')
  ident,count,blank=self.store.add_document(p,'/missing/ocr');self.assertEqual(count,1)
  self.app.online=False;results=self.app.call_tool('search_library',{'query':'hearing September'});self.assertEqual(len(results),1);self.assertIn('postponed',results[0]['text'])
  pages=self.app.read_document_pages(results[0]['id'],1,1);self.assertIn('postponed',pages[0]['text'])
  self.assertEqual(self.store.add_document(p,'/missing/ocr')[1],0)
  self.store.forget_document(ident);self.assertTrue(p.exists());self.assertEqual(self.store.search('September'),[])
 def test_preferences_commands_and_mode(self):
  class Prompt:
   def prompt(self,q):return 'y'
  with contextlib.redirect_stdout(io.StringIO()):
   self.assertTrue(f.handle(self.app,'/remember Use short paragraphs',Prompt(),e.console,e.user_path))
   self.assertIn('Use short paragraphs',self.app.messages[0]['content'])
   self.assertTrue(f.handle(self.app,'/fast',Prompt(),e.console,e.user_path));self.assertEqual(self.app.mode,'fast')
   f.handle(self.app,'/forget all',Prompt(),e.console,e.user_path);self.assertNotIn('Use short paragraphs',self.app.messages[0]['content'])
  with self.assertRaises(ValueError):f.handle(self.app,'/remember password example',Prompt(),e.console,e.user_path)
 def test_keychain_metadata_has_no_secret(self):
  c=f.Credentials(self.store.root)
  class Backend:
   def set_password(self,*args):self.args=args
  b=Backend()
  with patch.object(c,'backend',return_value=b),patch('builtins.input',return_value='test@example.invalid'),patch('getpass.getpass',return_value='x'*30):
   self.assertTrue(c.enroll('courtlistener'))
  self.assertNotIn('x'*30,c.path.read_text(encoding='utf-8'));self.assertEqual(b.args,('local.envyterminal.courtlistener','test@example.invalid','x'*30))
  if os.name=='nt':f.verify_windows_sddl(f.windows_sddl(c.path),f.windows_user_sid(),is_dir=False)
  else:self.assertEqual(c.path.stat().st_mode&0o777,0o600)
  with patch.object(f.sys,'platform','unsupported'),patch.object(f.os,'name','posix'):
   with self.assertRaises(RuntimeError):c.backend()
 def test_citation_audit(self):
  self.app.add_source('Snippet','https://example.invalid','summary','search snippet — not verified')
  self.app.messages.append({'role':'assistant','content':'claim [S1] and [S999]'})
  capture=io.StringIO()
  from rich.console import Console
  with patch.object(e,'console',Console(file=capture,force_terminal=False,width=200)):self.app.audit()
  self.assertIn('SEARCH SNIPPET ONLY',capture.getvalue());self.assertIn('MISSING source',capture.getvalue())
if __name__=='__main__':unittest.main()
