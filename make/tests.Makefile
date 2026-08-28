curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

# Tests automatisés
dir_tests = tests
pytest = $(pipenv) run pytest
clangformat = /usr/local/bin/clang-format
ard_src = src/arduino

pytest: python
	$(pytest)

twinetest: python $(sdist) $(wheel)
	$(twine) upload -r testpypi $(sdist)/* $(wheel)/* 2> "$(LOGS)/$(notdir $@).log"

ruff = $(pipenv) run ruff
rufffiles = $(wildcard src/xphs1903/**/*.py) $(wildcard template/**/*.py) $(wildcard docs/**/*.py) $(wildcard tests/**/*.py)
ruffcheck: pipenv
	$(ruff) check $(rufffiles) 2> "$(LOGS)/$(notdir $@).log"

rufflint: pipenv
	$(ruff) check -v --fix $(rufffiles) 2> "$(LOGS)/$(notdir $@).log"

ruffformat: pipenv
	$(ruff) format -v $(rufffiles) 2> "$(LOGS)/$(notdir $@).log"

black = $(pipenv) run black
blackfiles = $(wildcard src/xphs1903/**/*.py) $(wildcard template/**/*.py) $(wildcard docs/**/*.py) $(wildcard tests/**/*.py)
blackformat: pipenv
	$(black) $(blackfiles)

pylint = $(pipenv) run pylint
pylintfiles = $(wildcard src/xphs1903/**/*.py) $(wildcard template/**/*.py) $(wildcard docs/**/*.py) $(wildcard tests/**/*.py)
pylint: pipenv
	$(pylint) $(pylintfiles)

clangformat: $(clangformat)
	$(clangformat) -i $(ard_src)/**/*.{ino,h,cpp} 2> "$(LOGS)/$(notdir $@).log"

format: ruffformat blackformat clangformat

lint: format rufflint pylint

$(clangformat):
	[[ -x $@ ]]

$(info $(curr_mk) lu.)
