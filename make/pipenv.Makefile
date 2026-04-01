# Développement
pipfile = Pipfile
pipfile_lock = Pipfile.lock
prerequis = .build/requirements.txt
venv = .venv

$(pipfile_lock): $(pipfile) pipenv
	$(pipenv) verify

# On ne veut pas accidentellement mettre à jour Pipfile.lock
# Ça pourrait introduire des vulnérabilités dans le code.
lock: $(pipfile) pipenv
	$(pipenv) lock

$(venv): $(pipfile_lock)
	$(pipenv) sync

drapeau_pip = $(DIR_DRAPEAUX)/pip
pip: $(drapeau_pip)

$(drapeau_pip): $(python) $(DIR_DRAPEAUX)
	$(python) -m ensurepip
	$(pip) install --upgrade pip
	$(touch) $@

drapeau_pipenv = $(DIR_DRAPEAUX)/pipenv
pipenv: $(drapeau_pipenv)

$(drapeau_pipenv): pip $(DIR_DRAPEAUX)
	$(pip) install --upgrade pipenv
	$(touch) $@

$(prerequis): $(pipfile)
	$(pipenv) requirements --exclude-index --no-lock|sed 's/==/~=/g' > $@