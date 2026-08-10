# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Small script to get the version for compatible with Python wheels."""

from datetime import date
from subprocess import run
from pathlib import Path

DEFAULT_REPO = (Path(__file__).parent.parent / '.git').resolve()

def version(repo_path: Path = DEFAULT_REPO):
    reference = run(
        ['/usr/bin/git', 'describe', '--always'],
        capture_output=True,
        check=True,
    ).stdout.decode('utf-8')
    release = reference.strip().lstrip('v')

    version, steps, commit = '', '', ''
    if '-' in release:
        version, *commit = release.split('-')
    else:
        version = release

    if commit:
        commit = f'+{commit[-1]}'

    return version, commit

def currdate():
    d = date.today()
    return f'.d{d:%Y%m%d}'

def vstring():
    v, c = version()
    d = currdate()

    if c:
        return f'{v}{c}{d}'
    else:
        return v

def main():
    print(vstring())

if __name__ == '__main__':
    main()
