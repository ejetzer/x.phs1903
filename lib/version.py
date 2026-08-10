# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Small script to get the version for compatible with Python wheels."""

from datetime import UTC, date, datetime
from pathlib import Path
from subprocess import run  # noqa: S404

DEFAULT_REPO = (Path(__file__).parent.parent / '.git').resolve()


def version(repo_path: Path = DEFAULT_REPO) -> tuple[str, str]:
    """Cherche la version selon git.

    Returns
    ------------------
    version: str
        Le tag de version.
    commit: str
        Le commit si le répertoire a avancé.
    """
    reference = run(  # noqa: S603
        ['/usr/bin/git', '-C', str(repo_path), 'describe', '--always'],
        capture_output=True,
        check=True,
    ).stdout.decode('utf-8')
    release = reference.strip().lstrip('v')

    version, commit = '', ''
    if '-' in release:
        version, *commit = release.split('-')
    else:
        version = release

    if commit:
        commit = f'+{commit[-1]}'

    return version, commit


def currdate() -> date:
    """Calcule la date pour la version.

    Returns
    ------------------
    d: datetime.date
        Today's date formatted for a version string.
    """
    d = datetime.now(tz=UTC).date()
    return f'.d{d:%Y%m%d}'


def vstring() -> str:
    """Calcule la version du projet.

    Returns
    ------------------
    version: str
        La version compatible avec les noms de wheel.
    """
    v, c = version()
    d = currdate()

    if c:
        return f'{v}{c}{d}'

    return v


def main() -> None:
    """Affiche la version du projet."""
    print(vstring())


if __name__ == '__main__':
    main()
