import importlib.util
import json
from pathlib import Path
import shutil
import zipfile

import pytest

from pyshop.app_info import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('release_verifier', ROOT / 'tools/verify-release.py')
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


@pytest.fixture
def release(tmp_path):
    shutil.copytree(ROOT / 'assets', tmp_path / 'assets')
    for name in ('README.md', 'LICENSE', 'CHANGELOG.md'):
        shutil.copy2(ROOT / name, tmp_path / name)
    executable = tmp_path / 'PyShop.exe'
    executable.write_bytes(b'package validation fixture')
    report = {
        'schemaVersion': 1, 'version': APP_VERSION,
        'source': {'kind': 'Windows executable', 'sha256': verifier.digest(executable), 'sizeBytes': executable.stat().st_size},
        'environment': {'surface': 'isolated Windows desktop', 'temporaryProfile': True, 'sampleProject': True},
        'demoImage': {'sha256': verifier.digest(tmp_path / 'assets/demo/coastal-cabin.png')},
        'captures': [
            {'file': name, 'sha256': verifier.digest(tmp_path / 'assets/screenshots' / name),
             'sizeBytes': (tmp_path / 'assets/screenshots' / name).stat().st_size, 'width': 1600, 'height': 1000}
            for name in sorted(verifier.CAPTURES)
        ],
    }
    (tmp_path / 'assets/screenshots/capture-report.json').write_text(json.dumps(report), encoding='utf-8')
    return tmp_path, executable


def test_originals_match_the_recorded_masters():
    for name, expected in verifier.ORIGINALS.items():
        assert verifier.digest(ROOT / 'assets/brand/concepts' / name) == expected


def test_complete_package_passes(release):
    root, executable = release
    archive = root / 'package.zip'
    files = [file for file in root.rglob('*') if file.is_file()]
    with zipfile.ZipFile(archive, 'w') as package:
        for file in files:
            package.write(file, file.relative_to(root).as_posix())
    assert verifier.verify(root, executable, APP_VERSION, archive)['archiveVerified']


@pytest.mark.parametrize('damage, message', [
    ('missing_image', 'Missing local document asset'),
    ('changed_concept', 'Original concept changed'),
    ('changed_capture', 'Capture changed'),
    ('changed_executable', 'Captures do not match'),
    ('stale_version', 'Capture version is stale'),
    ('missing_capture', 'Expected four product captures'),
])
def test_invalid_marketing_delivery_is_rejected(release, damage, message):
    root, executable = release
    report_path = root / 'assets/screenshots/capture-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if damage == 'missing_image':
        (root / 'assets/brand/pyshop-readme-banner.png').unlink()
    elif damage == 'changed_concept':
        (root / 'assets/brand/concepts/direction-02-selected-layered-aperture.png').write_bytes(b'changed')
    elif damage == 'changed_capture':
        (root / 'assets/screenshots/02-layered-edit.png').write_bytes(b'changed')
    elif damage == 'changed_executable':
        executable.write_bytes(b'changed')
    elif damage == 'stale_version':
        report['version'] = '0.0.0'
    elif damage == 'missing_capture':
        report['captures'].pop()
    report_path.write_text(json.dumps(report), encoding='utf-8')
    with pytest.raises(ValueError, match=message):
        verifier.verify(root, executable, APP_VERSION)


def test_zip_without_readme_artwork_is_rejected(release):
    root, executable = release
    archive = root / 'package.zip'
    with zipfile.ZipFile(archive, 'w') as package:
        package.write(executable, 'PyShop.exe')
    with pytest.raises(ValueError, match='ZIP has missing'):
        verifier.verify(root, executable, APP_VERSION, archive)
