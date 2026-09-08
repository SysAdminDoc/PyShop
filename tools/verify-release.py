#!/usr/bin/env python3
"""Check the artwork, capture provenance, and portable release contents."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from PIL import Image

CAPTURES = {'01-welcome.png', '02-layered-edit.png', '03-analysis.png', '04-selection.png'}
ORIGINALS = {
    'direction-01-demo-coastal-photo.png': '82668cc8b5fb7d0bfcc07da3014053fec9c6ce2c299db4ed7dbfb7e51bdf0097',
    'direction-02-selected-layered-aperture.png': 'b68e396faf3928f0235d724ad1a7b46a84e110cb15e475dbcbb109f24b203cbf',
    'direction-03-layered-aperture-light.png': '894de8969b35513955c9ff9590b477518215afc55c60373c766ae69177aa7f20',
    'direction-04-layered-aperture-diamond.png': 'ed0c7e4c036e51abd6efae70000dfb24405d3a9398056aa7f1d51276c795f217',
    'direction-05-layered-aperture-app-icon.png': '805c6dbc9e58627a3b7b392dc94ef26031924bf112bbf4b2dd4671c2901035d1',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def verify_links(root):
    count = 0
    for document in (root / 'README.md', root / 'assets/brand/concepts/README.md'):
        text = document.read_text(encoding='utf-8')
        links = re.findall(r'(?:src|href)="([^"]+)"|\]\(([^)]+)\)', text)
        for match in links:
            link = (match[0] or match[1]).split('#')[0]
            if not link or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', link):
                continue
            target = (document.parent / link).resolve()
            require(target.is_relative_to(root.resolve()) and target.is_file(), f'Missing local document asset: {link}')
            count += 1
    return count


def verify_capture(root, executable, version):
    screenshots = root / 'assets/screenshots'
    report = json.loads((screenshots / 'capture-report.json').read_text(encoding='utf-8'))
    require(report['schemaVersion'] == 1 and report['version'] == version, 'Capture version is stale')
    source = report['source']
    require(source['kind'] == 'Windows executable' and source['sha256'] == digest(executable), 'Captures do not match this executable')
    require(source['sizeBytes'] == executable.stat().st_size, 'Executable size changed')
    require(report['environment'] == {'surface': 'isolated Windows desktop', 'temporaryProfile': True, 'sampleProject': True}, 'Capture environment is incomplete')
    require(report['demoImage']['sha256'] == digest(root / 'assets/demo/coastal-cabin.png'), 'Sample image changed')
    require(len(report['captures']) == 4 and {item['file'] for item in report['captures']} == CAPTURES, 'Expected four product captures')
    for record in report['captures']:
        path = screenshots / record['file']
        require(record['sha256'] == digest(path) and record['sizeBytes'] == path.stat().st_size, f'Capture changed: {path.name}')
        with Image.open(path) as image:
            require(image.size == (1600, 1000) == (record['width'], record['height']), f'Unexpected capture size: {path.name}')
            image.verify()


def verify(root, executable, version, archive=None):
    concepts = root / 'assets/brand/concepts'
    for name, expected in ORIGINALS.items():
        require(digest(concepts / name) == expected, f'Original concept changed: {name}')
    require(digest(root / 'assets/brand/pyshop-selected-master.png') == ORIGINALS['direction-02-selected-layered-aperture.png'], 'Selected master changed')
    require(digest(root / 'assets/brand/pyshop-icon-small-master.png') == ORIGINALS['direction-05-layered-aperture-app-icon.png'], 'Optical master changed')
    links = verify_links(root)
    verify_capture(root, executable, version)
    readme = (root / 'README.md').read_text(encoding='utf-8')
    require(f'version-v{version}-' in readme and f'PyShop-v{version}-win64.zip' in readme, 'README version is stale')
    if archive:
        expected = {p.relative_to(root).as_posix(): p for p in (root / 'assets').rglob('*') if p.is_file()}
        expected.update({'PyShop.exe': executable, **{name: root / name for name in ('README.md', 'LICENSE', 'CHANGELOG.md')}})
        with zipfile.ZipFile(archive) as package:
            names = [item.filename.removeprefix('./') for item in package.infolist() if not item.is_dir()]
            require(len(names) == len(set(names)) and set(names) == set(expected), 'ZIP has missing or unexpected files')
            for item in package.infolist():
                if not item.is_dir():
                    name = item.filename.removeprefix('./')
                    require(hashlib.sha256(package.read(item)).hexdigest() == digest(expected[name]), f'ZIP content differs: {name}')
    return {'version': version, 'originalConcepts': len(ORIGINALS), 'productCaptures': 4, 'localDocumentLinks': links, 'archiveVerified': bool(archive)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.executable, args.version, args.archive), indent=2))
