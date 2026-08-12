# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Script d'exportation des rapports de bogue de Github."""

import argparse
import pathlib
import urllib.parse
from typing import TYPE_CHECKING

import pandoc
import requests

if TYPE_CHECKING:
    from typing import Final

__prog__ = "Export d'Issues Github à reST pour Sphinx"
__description__ = """
Télécharge les rapports de bogues de Github
pour les exporter dans un format reST
acceptable pour être intégré à de la
documentation Sphinx.
"""
__epilog__ = """
Par Émile Jetzer, pour le module x.phs1903
"""

args = argparse.ArgumentParser(
    prog=__prog__, description=__description__, epilog=__epilog__
)


class InvalidEndpointError(ValueError):
    """Mauvais appel d'API."""

    def __init__(self, endpoint: str) -> None:
        """Mauvais appel d'API."""
        msg: str = f'Endpoint {endpoint:r} is not valid.'
        super().__init__(msg)


class Github:
    """Interactions avec l'API de GitHub."""

    API_URL: Final[str] = 'https://api.github.com'
    """URL de l'API GitHub."""

    ENDPOINTS: tuple[str] = ('issues',)
    """Appels d'API gérés par la classe."""

    def __init__(self, token: str) -> None:
        """Création d'une :class:`requests.Session`."""
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/vnd.github+json'
        self.session.headers['X-GitHub-Api-Version'] = '2026-03-10'
        self.session.headers['Authorization'] = f'Bearer {token}'

    def url(self, endpoint: str, **kargs: int | str) -> str:
        """Calcule l'URL d'appel d'API.

        Returns
        ----------------
        str
            L'URL complète pour l'appel d'API.

        Raises
        ----------------
        InvalidEndpointError
            Si l'appel est invalide ou non-géré par la classe.
        """
        if endpoint in self.ENDPOINTS:
            params = ''
            if len(kargs) > 0:
                params = '?' + urllib.parse.urlencode(kargs)

            return f'{self.API_URL}/{endpoint}{params}'

        raise InvalidEndpointError(endpoint)

    def api(self, endpoint: str, **kargs: int | str) -> dict | None:
        """Appelle l'API GitHub.

        Returns
        ----------------
        dict
            Le résultat de la requête, produit à partir du JSON.
        """
        req = self.session.get(self.url(endpoint, **kargs))

        if req.ok:
            return req.json()

        req.raise_for_status()
        return None

    def issues(  # noqa: PLR0913
        self,
        *,
        filter: str = 'assigned',  # noqa: A002
        state: str = 'open',
        sort: str = 'created',
        labels: list[str] | None = None,
        direction: str = 'desc',
        since: str | None = None,
        collab: bool | None = None,
        orgs: bool | None = None,
        owned: bool | None = None,
        pulls: bool | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[Issue]:
        """Liste les rapports de problèmes accessibles pour l'utilisateur.

        Returns
        ----------------
        list[Issue]
            La liste des rapports disponibles.
        """
        kargs = {
            'filter': filter,
            'state': state,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page': page,
        }

        if labels is not None and len(labels) > 0:
            kargs['labels'] = ','.join(labels)
        if since is not None:
            kargs['since'] = str(int(since))
        if collab is not None:
            kargs['collab'] = str(int(collab))
        if orgs is not None:
            kargs['orgs'] = str(int(collab))
        if owned is not None:
            kargs['owned'] = str(int(owned))
        if pulls is not None:
            kargs['pulls'] = str(int(pulls))

        rep = self.api('issues', **kargs)

        return [Issue(self, **issue) for issue in rep]

    def __repr__(self) -> str:
        """Représente l'objet :class:`GitHub`.

        Returns
        ----------------
        str
            <API GitHub>
        """
        return '<API GitHub>'


class User:
    """Description d'un utilisateur de GitHub."""

    def __init__(
        self,
        parent: Github,
        /,
        login: str,
        id: int,  # noqa: A002
        node_id: str,
        url: str,
        **kargs: str | int | bool | None,  # noqa: ARG002
    ) -> None:
        """Analyse des paramètres."""
        self.parent: Final[Github] = parent
        self.id: Final[int] = id
        self.node_id: Final[str] = node_id
        self.login: Final[str] = login
        self.url: Final[str] = url

    def __repr__(self) -> str:
        """Représente un User.

        Returns
        ----------------
        str
        """
        return f'<User#{self.id} from {self.parent!r}>'

    def __str__(self) -> str:
        """Affiche un User.

        Returns
        ----------------
        str
        """
        return f'{self.login}#{self.id}'


class Repository:
    """Description d'un répertoire GitHub."""

    def __init__(  # noqa: PLR0913
        self,
        parent: Github,
        *,
        id: int,  # noqa: A002
        node_id: str,
        name: str,
        full_name: str,
        owner: dict,
        html_url: str,
        **kargs: str | int | bool | None,  # noqa: ARG002
    ) -> None:
        """Analyse des paramètres."""
        self.parent = parent
        self.id = id
        self.node_id = node_id
        self.name = name
        self.full_name = full_name
        self.html_url = html_url
        self.owner = User(parent, **owner)


class Issue:
    """Description d'un rapport de problème."""

    def __init__(  # noqa: PLR0913
        self,
        parent: Github,
        *,
        id: int,  # noqa: A002
        node_id: str,
        url: str,
        html_url: str,
        title: str,
        body: str,
        user: dict[str, str | int],
        repository: dict,
        **kargs: str | int | bool | None,  # noqa: ARG002
    ) -> None:
        """Analyse des paramètres."""
        self.parent: Final[Github] = parent
        self.id: Final[int] = id
        self.node_id: Final[str] = node_id
        self.title: Final[str] = title
        self.url: Final[str] = url
        self.html_url: Final[str] = html_url

        if body is None:
            self.__body: Final[str] = ''
        else:
            self.__body: Final[str] = body

        self.user: Final[User] = User(parent, **user)
        self.repository: Final[Repository] = Repository(parent, **repository)

    @property
    def body(self) -> str:
        """Converti le contenu en reST.

        Returns
        ----------------
        rst: str
            Le texte converti.
        """
        mod = pandoc.read(self.__body, format='gfm')
        return pandoc.write(mod, format='rst')

    def __repr__(self) -> str:
        """Représente une Issue.

        Returns
        ----------------
        str
        """
        return f'<Issue#{self.id} by {self.user} from {self.parent}>'

    def __str__(self) -> str:
        """Affiche une description de l'Issue.

        Returns
        ----------------
        str
        """
        return f'Issue#{self.id} by {self.user}'

    def to_rst(self) -> str:
        """Converti en reST.

        Returns
        ----------------
        str
        """
        title: str = self.title
        title_line: str = '.' * (len(title) + 2)
        ret: str = f"""
{title}
{title_line}

Voir en ligne: {self.html_url}.

{self.body}
        """

        return ret


def main() -> None:
    """Affiche une section reST des rapports de problème."""
    token = (
        (pathlib.Path.home() / '.config' / 'github' / 'tokens' / 'issues.txt')
        .read_text()
        .strip()
    )
    gh = Github(token)
    issues = gh.issues()

    print('Rapports de bogues sur Github')
    print('----------------------------------')
    print()
    print()
    for issue in issues:
        if issue.repository.name == 'x.phs1903':
            print(issue.to_rst())


if __name__ == '__main__':
    main()
