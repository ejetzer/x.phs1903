# Configuration générale
SHELL = /bin/sh
SOURCE = src
README = README.rst

# Code source
dir_source_python = $(SOURCE)/xphs1903
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

build: .build/xphs1903.zip

help:
	@echo "Fichier de compilation de module Arduino"

.build:
	mkdir -p $@

.build/arduino: .build
	mkdir -p $@

.build/arduino/src .build/arduino/examples: .build/arduino
	mkdir -p $@

.build/arduino/src/xphs1903.h: .build/arduino/src/%: src/arduino/% .build/arduino/src
	cp $< $@
	
.build/arduino/examples/freq_adc .build/arduino/examples/annonceur: .build/arduino/examples/%: tests/% .build/arduino/examples
	cp -r $< $@

.build/arduino/arduino.yaml .build/arduino/keywords.txt .build/arduino/library.properties: .build/arduino/%: % .build
	cp $< $@

clean:
	-rm -rf .build/arduino

wipe:
	-rm -rf .build/arduino
	-rm -rf .build/xphs1903.zip

.build/xphs1903.zip: .build/arduino/src/xphs1903.h .build/arduino/examples/freq_adc .build/arduino/examples/annonceur .build/arduino/arduino.yaml .build/arduino/keywords.txt .build/arduino/library.properties
	cp -r .build/arduino/ .build/xphs1903/
	[[ -e $@ ]] && tar -uf $@ -C .build/ xphs1903/ || tar -cf $@ -C .build/ xphs1903/
	rm -rf .build/xphs1903/

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

