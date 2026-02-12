dir_source_python = $(SOURCE)/xphs1903

# Développement
pipfile = Pipfile
pipfile_lock = Pipfile.lock
prerequis = requirements.txt

# Configuration de module Python
pyproject = pyproject.toml

python_build = $(BUILD)/dist
python_wheel = $(BUILD)/wheel

## Compiler et installer le module Python
python: $(dir_source_python) $(pyproject) pipenv
	$(pipenv) install --user .

$(python_build): $(dir_source_python) $(pyproject)
	$(pipenv) run python -m build --sdist --outdir=$@

$(python_wheel): $(python_build)
	$(pipenv) run python -m build --wheel --outdir=$@
