"""Check the size and SHA-256 of every entry in this distribution."""
import hashlib
import json
from pathlib import Path

def verify(root):
    root=root.resolve()
    manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    seen=set()
    for record in manifest['files']:
        path=(root/record['path']).resolve()
        if not path.is_relative_to(root) or path in seen:
            raise ValueError('Invalid or duplicate manifest entry: '+record['path'])
        seen.add(path)
        with path.open('rb') as stream:
            checksum=hashlib.file_digest(stream,'sha256').hexdigest()
        if path.stat().st_size != record['size_bytes'] or checksum != record['sha256']:
            raise ValueError('File differs from the manifest: '+record['path'])
    print(f"Verified {len(seen)} files in {manifest['distribution']}.")
if __name__=='__main__':
    verify(Path(__file__).resolve().parent)
