"""Portable ancillary checks: contrast pairs, relative result paths, concepts, gzip."""
from pathlib import Path
import json
import gzip
ROOT = Path(__file__).resolve().parents[1]

def luminance(color):
    values = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    return sum(weight*(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4)
               for weight,v in zip((.2126,.7152,.0722), values))

pairs = [('#243d2e', '#fafaf5'), ('#667168', '#fafaf5'), ('#556b49', '#fafaf5'),
         ('#597342', '#fafaf5'), ('#ffffff', '#255c42'), ('#586e41', '#fffef9'),
         ('#66715e', '#fafaf5'), ('#9d3425', '#fdf0e9'), ('#667168', '#f1f3e9')]
checks = []
for foreground, background in pairs:
    a,b = sorted([luminance(foreground), luminance(background)])
    contrast = (b+.05)/(a+.05)
    checks.append({'foreground': foreground, 'background': background,
                   'ratio': round(contrast, 2), 'minimum': 4.5, 'passed': contrast >= 4.5})
assert all(check['passed'] for check in checks), checks
(ROOT/'ДЗ4/contrast-checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
results_path = ROOT/'ДЗ4/test-results.json'
results = json.loads(results_path.read_text(encoding='utf-8'))
for suite in results['testResults']:
    suite['name'] = 'frontend/tests/' + Path(suite['name']).name
results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
assets = sorted((ROOT/'frontend/dist/assets').glob('*'))
gzip_bytes = sum(len(gzip.compress(p.read_bytes(), compresslevel=6, mtime=0)) for p in assets if p.suffix in {'.js', '.css'})
assert gzip_bytes <= 350000
build = {'gzipBytes': gzip_bytes, 'limitBytes': 350000, 'passed': True,
         'assets': [p.name for p in assets if p.suffix in {'.js', '.css'}]}
(ROOT/'ДЗ4/build-check.json').write_text(json.dumps(build, indent=2), encoding='utf-8')
concepts = list((ROOT/'ДЗ3/ui_concepts').glob('concept-*.html'))
assert len(concepts) == 3 and len({p.read_bytes() for p in concepts}) == 3
print(json.dumps({'contrastPairsPassed': len(checks), 'concepts': len(concepts),
                  'testsPassed': results['numPassedTests'], 'gzipBytes': gzip_bytes}))
