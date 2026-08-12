# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Small script to get the version for compatible with Python wheels."""

from datetime import UTC, date, datetime
from pathlib import Path
from subprocess import run  # noqa: S404

DEFAULT_REPO = (Path(__file__).parent.parent).resolve()


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


base = Path(__file__).parent.parent.resolve()
FICHIERS_VERSION = (
    base / 'cfg' / 'library.json',
    base / 'cfg' / 'library.properties',
    base / 'template' / 'requirements.txt',
)


def cfgver(fichiers: tuple[Path] = FICHIERS_VERSION) -> None:
    """Mets à jour la version dans des documents de configuration.

    Raises
    ------------------
    ValueError
        Si le type de fichier n'est pas reconnu.
    """
    v, _ = version()

    for fichier in fichiers:
        nom = fichier.stem
        ext = fichier.suffix.strip('.')

        if ext == 'json':
            # Fichier de description de librairie Arduino
            import json  # noqa: PLC0415

            doc = json.loads(fichier.read_text())
            doc['version'] = v
            fichier.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        elif ext == 'properties':
            doc = fichier.read_text().split('\n')
            for idx, ligne in enumerate(doc):
                if ligne.startswith('version='):
                    doc[idx] = f'version={v}'
            doc = '\n'.join(doc)
            fichier.write_text(doc)
        elif nom == 'requirements':
            doc = fichier.read_text().split('\n')
            for idx, ligne in enumerate(doc):
                if ligne.startswith('x.phs1903'):
                    doc[idx] = f"x.phs1903=={v}; python_version == '3.14'"
            doc = '\n'.join(doc)
            fichier.write_text(doc)
        else:
            msg = 'Type de fichier invalide'
            raise ValueError(msg)


def upverse(
    repo_path: Path = DEFAULT_REPO,
    fichiers_version: tuple[Path] = FICHIERS_VERSION,
) -> None:
    """Mets à jour la micro-version du projet."""
    v, _ = version()
    s = vstring()

    if v != s:
        major, minor, mini = map(int, v.split('.'))
        mini += 1
        tag = f'v{major}.{minor}.{mini}'
        commentaire = input('>>>')
        ps = run(  # noqa: S603
            [
                '/usr/bin/git',
                '-C',
                str(repo_path),
                'tag',
                tag,
                '-m',
                commentaire,
            ],
            capture_output=True,
            check=True,
        )
        print(ps.stdout.decode('utf-8'))

        cfgver()

        ps = run(  # noqa: S603
            ['/usr/bin/git', '-C', str(repo_path), 'add', '-f']
            + list(map(str, fichiers_version)),
            capture_output=True,
            check=True,
        )
        print(ps.stdout.decode('utf-8'))

        ps = run(  # noqa: S603
            [
                '/usr/bin/git',
                '-C',
                str(repo_path),
                'commit',
                '-m',
                commentaire,
            ],
            capture_output=True,
            check=True,
        )
        print(ps.stdout.decode('utf-8'))

        ps = run(  # noqa: S603
            [
                '/usr/bin/git',
                '-C',
                str(repo_path),
                'tag',
                '-f',
                tag,
                '-m',
                commentaire,
            ],
            capture_output=True,
            check=True,
        )
        print(ps.stdout.decode('utf-8'))


def main() -> None:
    """Affiche la version du projet."""
    import sys  # noqa: PLC0415

    if len(sys.argv) > 1 and sys.argv[1] == '--upverse':
        upverse()

    cfgver()
    print(vstring())


if __name__ == '__main__':
    main()
