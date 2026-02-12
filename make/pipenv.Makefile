Pipfile.lock: Pipfile pipenv
	$(pipenv)
	$(pipenv) install
	$(pipenv) lock
	$(pipenv) sync

Pipfile:

drapeau_pip = $(DIR_DRAPEAUX)/pip
pip: $(drapeau_pip)

$(drapeau_pip): $(python) $(DIR_DRAPEAUX)
	$(python) -m ensurepip
	$(touch) $@

drapeau_pipenv = $(DIR_DRAPEAUX)/pipenv
pipenv: $(drapeau_pipenv)

$(drapeau_pipenv): pip $(DIR_DRAPEAUX)
	$(pip) install --user pipenv
	$(touch) $@
