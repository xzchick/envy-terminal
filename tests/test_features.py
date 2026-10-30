import tempfile,unittest,json,io,contextlib
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
  self.store.save('example',self.app);raw=(self.store.sessions/'example.json').read_text();self.assertNotIn('secret-token',raw)
  other=e.Research(self.store);self.store.load('example',other);self.assertEqual(other.messages[-1]['content'],'hello');self.assertFalse(other.online);self.assertEqual(other.mode,'fast');self.assertEqual(other.allowed_files,{'/a/file.pdf'});self.assertIsNone(other.court_token)
  self.store.delete_chat('example');self.assertEqual(self.store.chats(),[])
 def test_private_storage_and_traversal(self):
  self.assertEqual(self.store.root.stat().st_mode&0o777,0o700)
  with self.assertRaises(ValueError):self.store.save('../../escape',self.app)
  self.store.save('safe',self.app);self.assertEqual((self.store.sessions/'safe.json').stat().st_mode&0o777,0o600)
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
  self.assertNotIn('x'*30,c.path.read_text());self.assertEqual(b.args,('local.envyterminal.courtlistener','test@example.invalid','x'*30))
 def test_citation_audit(self):
  self.app.add_source('Snippet','https://example.invalid','summary','search snippet — not verified')
  self.app.messages.append({'role':'assistant','content':'claim [S1] and [S999]'})
  capture=io.StringIO()
  from rich.console import Console
  with patch.object(e,'console',Console(file=capture,force_terminal=False,width=200)):self.app.audit()
  self.assertIn('SEARCH SNIPPET ONLY',capture.getvalue());self.assertIn('MISSING source',capture.getvalue())
if __name__=='__main__':unittest.main()
