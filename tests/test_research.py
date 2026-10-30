import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from envy_terminal import cli, features

class ResearchTests(unittest.TestCase):
 def test_private_web_addresses_rejected(self):
  address=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',80))]
  with patch.object(socket,'getaddrinfo',return_value=address):
   with self.assertRaises(ValueError):cli.validate_url('http://example.invalid/private')
 def test_url_credentials_rejected(self):
  with self.assertRaises(ValueError):cli.validate_url('https://user:password@example.invalid/')
 def test_paid_pacer_not_automated(self):
  with self.assertRaises(ValueError):cli.validate_url('https://pcl.uscourts.gov/')
 def test_offline_denies_web(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=features.LocalStore(Path(tmp));app=cli.Research(store);app.online=False
   self.assertFalse(app.call_tool('web_search',{'query':'test'})['access_succeeded'])
   self.assertFalse(app.call_tool('read_url',{'url':'https://example.invalid/'})['access_succeeded'])
   store.db.close()
 def test_library_range_clamped_at_end(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=features.LocalStore(Path(tmp)/'data');p=Path(tmp)/'test.txt';p.write_text('A fictional record for testing.')
   store.add_document(p,'/nonexistent');app=cli.Research(store)
   result=app.library_search('fictional')[0]
   self.assertEqual(len(app.read_document_pages(result['id'],1,20)),1)
   with self.assertRaises(ValueError):app.read_document_pages(result['id'],2,1)
   store.db.close()
if __name__=='__main__':unittest.main()
