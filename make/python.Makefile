dir_source_python = $(SOURCE)/xphs1903

# Configuration de module Python
pyproject = pyproject.toml

sdist = $(BUILD)/sdist
wheel = $(BUILD)/wheel

## Compiler et installer le module Python
python: $(dir_source_python) $(pyproject) pipenv
	$(pipenv) install .

$(sdist): $(dir_source_python) $(pyproject)
	$(pipenv) run python -m build --sdist --outdir=$@

sdist: $(sdist)

$(wheel): $(python_build)
	$(pipenv) run python -m build --wheel --outdir=$@

wheel: $(wheel)