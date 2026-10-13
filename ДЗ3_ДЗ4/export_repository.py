"""Read-only export for uploading reviewed homework files through the GitHub connector."""
from pathlib import Path
import base64
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent
SKIP = {'.git', 'node_modules', 'dist', '.sites-runtime', '.openai-state', '__pycache__'}
files = sorted(p for p in ROOT.rglob('*') if p.is_file()
               and not SKIP.intersection(p.relative_to(ROOT).parts)
               and not p.name.endswith(('.tar.gz', '.zip')))
def entry(p):
    return {'path': p.relative_to(ROOT).as_posix(), 'mode': '100644', 'type': 'blob'}
if sys.argv[1] == 'text':
    small = [p for p in files if p.suffix not in {'.jpg', '.png'} and p.stat().st_size < 50000]
    if len(sys.argv) > 2:
        small = small[int(sys.argv[2]):int(sys.argv[2])+5]
    output = [{**entry(p), 'content': p.read_text(encoding='utf-8')} for p in small]
elif sys.argv[1] == 'large':
    output = [{**entry(p), 'bytes': p.stat().st_size} for p in files
              if p.suffix in {'.jpg', '.png'} or p.stat().st_size >= 50000]
elif sys.argv[1] == 'blob':
    p = (ROOT / sys.argv[2]).resolve()
    assert p in files
    data = p.read_bytes()
    if len(sys.argv) > 3:
        offset, length = map(int, sys.argv[3:5])
        data = data[offset:offset+length]
    output = {**entry(p), 'content': base64.b64encode(data).decode('ascii')}
else:
    raise SystemExit('Use text, large, or blob PATH')
print(json.dumps(output, ensure_ascii=False))
