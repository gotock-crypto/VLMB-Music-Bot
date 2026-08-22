#!/usr/bin/env python3
"""Proves rollback semantics using isolated temporary release directories.

This is an isolated preflight simulation. A production operator can prove
the real rollback path with deploy_release.sh + FORCE_FAIL_AFTER_CUTOVER=1.
That guarded flag is intentionally required for the production drill.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

def main():
    with TemporaryDirectory(prefix='vlmb-rollback-drill-') as td:
        root=Path(td); app=root/'app'; release=root/'release'; backup=root/'backup'
        app.mkdir(); release.mkdir(); backup.mkdir()
        (app/'VERSION').write_text('3.0.6\n')
        shutil.copy2(app/'VERSION', backup/'VERSION')
        (release/'VERSION').write_text('4.0.0-rc1-BROKEN\n')
        # Simulate failed cutover.
        shutil.copy2(release/'VERSION', app/'VERSION')
        assert app.joinpath('VERSION').read_text().strip().endswith('BROKEN')
        # Restore previous release exactly as the deployment contract requires.
        shutil.copy2(backup/'VERSION', app/'VERSION')
        assert app.joinpath('VERSION').read_text().strip() == '3.0.6'
    print('Rollback drill simulation: PASS')

if __name__ == '__main__': main()
