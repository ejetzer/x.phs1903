curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

# Développement
pipfile = Pipfile
pipfile_lock = Pipfile.lock
prerequis ?= $(BUILD)/requirements.txt
prerequis_docs ?= $(BUILD)/requirements.txt
venv ?= .venv

$(pipfile_lock): $(pipfile) pipenv
	$(pipenv) verify 2> "$(LOGS)/$(notdir $@).log"

# On ne veut pas accidentellement mettre à jour Pipfile.lock
# Ça pourrait introduire des vulnérabilités dans le code.
lock: $(pipfile) pipenv
	$(pipenv) lock 2> "$(LOGS)/$(notdir $@).log"

$(venv): $(pipfile_lock)
	$(pipenv) sync 2> "$(LOGS)/$(notdir $@).log"

drapeau_pip = $(DIR_DRAPEAUX)/pip
pip: $(drapeau_pip)

$(drapeau_pip): $(python) $(DIR_DRAPEAUX)
	$(python) -m ensurepip 2> "$(LOGS)/$(notdir $@).log"
	$(pip) install --upgrade pip 2> "$(LOGS)/$(notdir $@).log"
	$(touch) $@

drapeau_pipenv = $(DIR_DRAPEAUX)/pipenv
pipenv: $(drapeau_pipenv)

$(drapeau_pipenv): pip $(DIR_DRAPEAUX)
	$(pip) install --upgrade pipenv 2> "$(LOGS)/$(notdir $@).log"
	$(touch) $@

$(prerequis_docs): $(pipfile)
	$(pipenv) requirements --exclude-index --no-lock|sed 's/==/~=/g' > $@ 2> "$(LOGS)/$(notdir $@).log"


$(info $(curr_mk) lu.)
