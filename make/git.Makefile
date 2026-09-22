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

CURRBRANCH := $(shell $(git) branch --show-current)
VERBRANCH := $(subst -dev,,$(CURRBRANCH))
merge: commit upverse
	$(git) checkout $(VERBRANCH)
	$(git) rebase $(CURRBRANCH)
	$(git) checkout $(CURRBRANCH)

mainline: merge
	$(git) checkout main
	$(git) rebase $(VERBRANCH)
	$(git) checkout $(CURRBRANCH)
