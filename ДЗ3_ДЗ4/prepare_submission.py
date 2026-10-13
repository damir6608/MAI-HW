"""Validate deliverables and package this homework without dependency/runtime folders."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
SKIP = {'.git', 'node_modules', '.sites-runtime', '.openai-state', '__pycache__'}

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not SKIP.intersection(p.relative_to(ROOT).parts)
                  and not p.name.endswith(('.tar.gz', '.zip'))
                  and p.name != 'submission_manifest.json')

required = ['README.md', 'ДЗ3/project_description.md', 'ДЗ3/user_stories.md',
            'ДЗ3/technical_specification.md', 'ДЗ3/requirements.md', 'ДЗ3/ai_review.md',
            'ДЗ3/ui_concepts/concept-01-calm.html', 'ДЗ3/ui_concepts/concept-02-warm.html',
            'ДЗ3/ui_concepts/concept-03-planner.html', 'ДЗ4/development_report.md',
            'ДЗ4/test-results.json', 'frontend/package-lock.json', 'frontend/dist/index.html']
for name in required:
    assert (ROOT / name).is_file(), f'Missing {name}'
result = json.loads((ROOT/'ДЗ4/test-results.json').read_text(encoding='utf-8'))
assert result['success'] and result['numPassedTests'] >= 3 and result['numFailedTests'] == 0
items = files()
manifest = {'project': 'FoodTech HW3/HW4', 'passedTests': result['numPassedTests'],
            'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                       'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in items]}
manifest_path = ROOT / 'submission_manifest.json'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = ROOT.parent / 'ДЗ3_ДЗ4_FoodTech.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
    for path in [*items, manifest_path]:
        output.write(path, 'ДЗ3_ДЗ4/' + path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as output:
    assert output.testzip() is None
print(json.dumps({'archive': str(archive), 'files': len(items) + 1,
                  'bytes': archive.stat().st_size, 'testsPassed': result['numPassedTests']}, ensure_ascii=False))
