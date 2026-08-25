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
ruffcheck: pipenv
	$(ruff) check . 2> "$(LOGS)/$(notdir $@).log"

rufflint: pipenv
	$(ruff) check --fix . 2> "$(LOGS)/$(notdir $@).log"

ruffformat: pipenv
	$(ruff) format . 2> "$(LOGS)/$(notdir $@).log"

black = $(pipenv) run black
blackformat: pipenv
	$(black) src/xphs1903 docs/ template/ tests/

pylint: pipenv
	$(pylint) src/xphs1903 docs/ template/ tests/

clangformat: $(clangformat)
	$(clangformat) -i $(ard_src)/**/*.{ino,h,cpp} 2> "$(LOGS)/$(notdir $@).log"

format: blackformat clangformat

lint: format rufflint

$(clangformat):
	[[ -x $@ ]]
