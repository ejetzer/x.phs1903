# Tests automatisés
dir_tests = tests
pytest = $(pipenv) run pytest

pytest: python
	$(pytest)

twinetest: python $(sdist) $(wheel)
	$(twine) upload -r testpypi $(sdist)/* $(wheel)/*

ruff = $(pipenv) run ruff
ruffcheck: pipenv
	$(ruff) check

rufflint: pipenv
	$(ruff) check --fix

ruffformat: pipenv
	$(ruff) format
