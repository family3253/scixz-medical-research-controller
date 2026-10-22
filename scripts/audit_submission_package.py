from pathlib import Path
import argparse,json,re
ALLOWED_EXT={'.docx','.xlsx','.xls','.xlsm','.csv','.tsv','.tif','.tiff','.jpg','.jpeg','.png','.pdf'}
FORBIDDEN_EXT={'.md','.json','.py','.ps1','.sh','.log','.bak','.tmp','.zip','.rar'}
FORBIDDEN_NAME=re.compile(r'(^|[_-])(readme|audit|manifest|preflight|backup|working|private|cache|test)([_-]|\.|$)',re.I)

def audit(root):
 root=Path(root); findings=[]; files=[]
 if not root.exists(): return {'status':'FAIL','root':str(root),'files':[],'findings':['missing_root']}
 for p in sorted(root.rglob('*')):
  if not p.is_file(): continue
  rel=p.relative_to(root).as_posix(); files.append(rel)
  if p.name.startswith('.') or any(part.startswith('.') for part in p.relative_to(root).parts): findings.append(f'hidden_file:{rel}')
  if p.suffix.lower() in FORBIDDEN_EXT: findings.append(f'forbidden_extension:{rel}')
  if p.suffix.lower() not in ALLOWED_EXT: findings.append(f'unrecognized_extension:{rel}')
  if FORBIDDEN_NAME.search(p.name): findings.append(f'forbidden_internal_name:{rel}')
 return {'status':'PASS' if not findings else 'FAIL','root':str(root),'files':files,'findings':findings}

def main():
 ap=argparse.ArgumentParser(description='Audit a final journal upload package for internal artifacts.')
 ap.add_argument('path'); ap.add_argument('--out',default='')
 args=ap.parse_args(); result=audit(args.path); text=json.dumps(result,ensure_ascii=False,indent=2)
 if args.out: Path(args.out).write_text(text+'\n',encoding='utf-8'); print(f'wrote={args.out};status={result["status"]};files={len(result["files"])}')
 else: print(text)
 return 0 if result['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
