# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Script d'exportation des rapports de bogue de Github."""

import argparse
import json
import requests
import pathlib
import pandoc
import urllib.parse

__prog__ = 'Export d\'Issues Github à reST pour Sphinx'
__description__ = \
'''
Télécharge les rapports de bogues de Github
pour les exporter dans un format reST
acceptable pour être intégré à de la
documentation Sphinx.
'''
__epilog__ = \
'''
Par Émile Jetzer, pour le module x.phs1903
'''

args = argparse.ArgumentParser(
    prog=__prog__,
    description=__description__,
    epilog=__epilog__
)


class InvalidEndpointError(ValueError):

    def __init__(self, endpoint: str):
        msg: str = f'Endpoint {endpoint:r} is not valid.'
        super().__init__(msg)


class Github:
    API_URL: Final[str] = 'https://api.github.com'
    ENDPOINTS: tuple[str] = (
        'issues',
    )

    def __init__(self, token: str) -> None:
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/vnd.github+json'
        self.session.headers['X-GitHub-Api-Version'] = '2026-03-10'
        self.session.headers['Authorization'] = f'Bearer {token}'

    def url(self, endpoint: str, **kargs) -> str:
        if endpoint in self.ENDPOINTS:

            params = ''
            if len(kargs) > 0:
                params = '?' + urllib.parse.urlencode(kargs)

            return f'{self.API_URL}/{endpoint}{params}'
        else:
            raise InvalidEndpointError(endpoint)

    def api(self, endpoint: str, **kargs) -> dict:
        req = self.session.get(self.url(endpoint, **kargs))

        if req.ok:
            return req.json()
        else:
            req.raise_for_status()

    def issues(
        self,
        *,
        filter: str = 'assigned',
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
        page: int = 1
    ) -> list[Issue]:
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
        rep = [Issue(self, **issue) for issue in rep]

        return rep

    def __repr__(self):
        return '<github>'


class User:

    def __init__(
        self,
        parent: Github,
        /,
        login: str,
        id: int,
        node_id: str,
        avatar_url: str,
        gravatar_id: str,
        url: str,
        html_url: str,
        followers_url: str,
        following_url: str,
        gists_url: str,
        starred_url: str,
        subscriptions_url: str,
        organizations_url: str,
        repos_url: str,
        events_url: str,
        received_events_url: str,
        type: str,
        site_admin: bool,
        **kargs: str | int | bool | None
    ) -> None:
        self.parent: Final[Github] = parent
        self.id: Final[int] = id
        self.node_id: Final[str] = node_id
        self.login: Final[str] = login
        self.url: Final[str] = url

    def __repr__(self):
        return f'<User#{self.id} from {self.parent!r}>'

    def __str__(self):
        return f'{self.login}#{self.id}'

class Repository:

    def __init__(
        self,
        parent: Github,
        /,
        id: int,
        node_id: str,
        name: str,
        full_name: str,
        owner: dict,
        private: bool,
        html_url: str,
        **kargs
    ) -> None:
        self.parent = parent
        self.id = id
        self.node_id = node_id
        self.name = name
        self.full_name = full_name
        self.html_url = html_url
        self.owner = User(parent, **owner)

class Issue:

    def __init__(
        self,
        parent: Github,
        /,
        id: int,
        node_id: str,
        url: str,
        repository_url: str,
        labels_url: str,
        comments_url: str,
        events_url: str,
        html_url: str,
        number: int,
        state: str,
        title: str,
        body: str,
        user: dict[str, str | int],
        pinned_comment: str | None,
        labels: list[dict],
        assignees: list[dict],
        milestone: dict,
        locked: bool,
        active_lock_reason: str,
        comments: int,
        closed_at: str | None,
        created_at: str,
        updated_at: str,
        repository: dict,
        author_association: str,
        *,
        assignee: dict | None = None,
        pull_request: dict | None = None,
        **kargs: str | int | bool | None,
    ) -> None:
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
    def body(self):
        mod = pandoc.read(self.__body, format='gfm')
        rst = pandoc.write(mod, format='rst')
        return rst

    def __repr__(self) -> str:
        return f"<Issue#{self.id} by {self.user} from {self.parent}>"

    def __str__(self) -> str:
        return f"Issue#{self.id} by {self.user}"

    def to_rst(self) -> str:
        title: str = self.title
        title_line: str = '.' * (len(title)+2)
        ret: str = f'''
{title}
{title_line}

Voir en ligne: {self.html_url}.

{self.body}
        '''

        return ret

def main():
    token = (pathlib.Path.home() / '.config' / 'github' / 'tokens' / 'issues.txt').read_text().strip()
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
