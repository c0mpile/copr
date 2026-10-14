#!/usr/bin/python3 -I
"""Print RPM BuildRequires derived from an upstream meson.build.

Usage: gen-buildrequires.py <srcdir> [skipfile]

Only unconditional, required dependencies are emitted; optional/feature/fallback
dependencies and non-pkg-config things stay hand-written in the spec. Names in
<skipfile> (one per line, '#' comments) are never emitted.
"""
import json
import re
import subprocess
import sys

src = sys.argv[1]
skip = set()
if len(sys.argv) > 2:
    try:
        with open(sys.argv[2]) as f:
            skip = {l.split('#')[0].strip() for l in f} - {''}
    except FileNotFoundError:
        pass

out = subprocess.run(['meson', 'introspect', '--scan-dependencies', 'meson.build'],
                     cwd=src, capture_output=True, text=True, check=True).stdout
reqs = []
for d in json.loads(out):
    name = d['name']
    if d.get('required') is not True or d.get('conditional') or name in skip or name == 'threads':
        continue
    versions = d.get('version') or ['']
    for ver in versions:
        m = re.match(r'\s*(>=|<=|==|<|>|=)\s*(\S+)', ver)
        line = f'BuildRequires:  pkgconfig({name})'
        if m:
            line += f' {"=" if m.group(1) == "==" else m.group(1)} {m.group(2)}'
        reqs.append(line)

# A dependency declared more than once keeps the most constrained lines only.
seen = list(dict.fromkeys(reqs))
seen = [l for l in seen if not any(o != l and o.startswith(l + ' ') for o in seen)]
print('\n'.join(seen))
