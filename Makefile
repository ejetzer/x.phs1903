# Configuration générale
SHELL = /bin/sh
SOURCE = src
README = README.rst

# Code source
dir_source_python = $(SOURCE)/x.phs1903
dir_source_arduino = $(SOURCE)/arduino

# Développement
pipfile = Pipfile
pipfile_lock = Pipfile.lock
prerequis = requirements.txt

# Installation de modules
arduino_proprietes = library.properties

# Configuration de module Arduino
arduino_exemples = examples
arduino_extras = extras

# Configuration de module Python
pyproject = pyproject.toml

# Documentation
dir_docs = docs
docs_prerequis = $(dir_docs)/requirements.txt
dir_docs_source = $(dir_docs)/source
dir_docs_build = $(dir_docs)/_build
readthedocs = .readthedocs.yaml

# Tests automatisés
dir_tests = tests

# Programmes utilitaires
python_version = 3.14
python ?= python3.14
pip ?= $(python) -m pip
pipenv ?= $(python) -m pipenv

.PHONY: aide help all tout install installer arduino python dev alldocs pdfdocs\
	htmldocs publish publier

aide help:


all tout:


install installer:
	

arduino:


python:


dev:
	$(pipenv) --python $(PY_VER)

alldocs: pdfdocs htmldocs

pdfdocs:
	
htmldocs:

publish publier:
