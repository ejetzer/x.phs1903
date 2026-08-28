curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

dir_source_python = $(SOURCE)/xphs1903

# Configuration de module Python
pyproject = pyproject.toml

sdist_name ?= x_phs1903-$(VERSION).tar.gz
wheel_name ?= x_phs1903-$(VERSION)-py3-none-any.whl
sdist = $(BUILD)/sdist
wheel = $(BUILD)/wheel

build_requirements ?= $(BUILD)/requirements.txt

## Compiler et installer le module Python
python: $(wheel)/$(wheel_name)
	$(pip) install . 2> "$(LOGS)/$(notdir $@).log"

$(sdist)/$(sdist_name): $(dir_source_python) $(pyproject) $(BUILD)/requirements.txt
	-$(rm) $(sdist)/*.tar.gz
	$(pipenv) run python -m build --sdist --outdir=$(sdist) . 2> "$(LOGS)/$(notdir $@).log"
	mv $(sdist)/x_phs1903-*.tar.gz "$@"

sdist: $(sdist)/$(sdist_name)

$(wheel)/$(wheel_name): $(dir_source_python) $(pyproject) $(python_build) $(BUILD)/requirements.txt
	-$(rm) $(wheel)/*.whl
	$(pipenv) run python -m build --wheel --outdir=$(wheel) . 2> "$(LOGS)/$(notdir $@).log"
	mv $(wheel)/x_phs1903-*.whl "$@"

wheel: $(wheel)/$(wheel_name)


$(info $(curr_mk) lu.)
