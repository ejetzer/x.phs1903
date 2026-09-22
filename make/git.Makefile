commit: lint
	-$(git) commit

push: commit
	$(git) push --all origin
	$(git) push --all local
	$(git) push --tag origin
	$(git) push --tag local

pull: commit
	$(git) pull --all

status:
	$(pipenv) run version
	$(git) status
