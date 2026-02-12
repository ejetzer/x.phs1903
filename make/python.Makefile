dir_source_python = $(SOURCE)/xphs1903

# Développement
pipfile = Pipfile
pipfile_lock = Pipfile.lock
prerequis = requirements.txt

# Configuration de module Python
pyproject = pyproject.toml

## Compiler et installer le module Python
python: $(dir_source_python) $(pyproject) pipenv
	$(pipenv) install --user .