from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('audit_submission_package',Path(__file__).resolve().parents[1]/'scripts'/'audit_submission_package.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_clean_upload_dir_passes(tmp_path):
 (tmp_path/'manuscript.docx').write_bytes(b'x')
 (tmp_path/'figure.tiff').write_bytes(b'x')
 assert mod.audit(tmp_path)['status']=='PASS'

def test_internal_artifact_fails(tmp_path):
 (tmp_path/'README.md').write_text('internal')
 (tmp_path/'audit.json').write_text('{}')
 result=mod.audit(tmp_path)
 assert result['status']=='FAIL'
 assert any('forbidden' in x for x in result['findings'])
