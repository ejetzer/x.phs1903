#
#  Makefile
#  phs1903
#
#  Créé par Émile Jetzer
#  GPLv3+
#

VARS_OLD := $(.VARIABLES) # Pour ne pas documenter les variables d'environnement

## USAGE
##  
## 	make [aide]   	Afficher ce message
## 	make install  	Installer les modules Python et Arduino
## 	make batir    	Compiler les modules pour l'installation
##	make tests    	Lancer les tests automatiques des modules
## 	make develop   	Installer l'environnement de développement
##  

## INFORMATION GÉNÉRALE
##  
## Les modules pour Python et Arduino contenus dans ce répertoire
## sont conçus pour les étudiants de première session du cours
## PHS1903 de Polytechnique Montréal. Le développement est dirigé
## par Émile Jetzer & Jacques Massicotte. Pour plus d'informations,
## lisez le document README.rst.
NAME = xphs1903
VERSION = 2.0.0
AUTHOR = "Émile Jetzer" "Jacques Massicotte"
SHELL = /bin/sh
SOURCE = src
README = README.rst
BUILD = .build
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
##  

DIR_DRAPEAUX = .flagfiles # Pour les fichiers d'état

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
arduino_build = $(BUILD)
arduino_package = $(arduino_build)/$(NAME).zip
arduino_fichiers = $(arduino_proprietes) $(arduino_extras) $(arduino_exemples)
arduino_fichiers_source = $(wildcard $(dir_source_arduino)/*)

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
dir_outils ?= dev
python_version ?= 3.14
python ?= /usr/local/bin/python3.14
pip ?= $(python) -m pip
pipenv ?= $(python) -m pipenv
arduino-cli ?= $(dir_outils)/arduino-cli
arduino-cli_url = https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh
curl ?= /usr/bin/curl
tar ?= /usr/bin/tar

# Raccourcis pratiques
dirs = $(DIR_DRAPEAUX) $(dir_docs_build) $(dir_outils) $(BUILD)

# Les répertoires d'installation ne faisant pas partie du répertoire
# git doivent pouvoir être créés sur le vif
$(dirs):
	mkdir -p $@

.PHONY: aide help all tout install installer arduino python develop alldocs\
	pdfdocs htmldocs publish publier build batir

## INSTALLATION
##  
## L'installation des modules se fait avec les gestionnaires de paquet
## par défaut pour les environnements correspondants. Le module Python
## s'installe avec pip, et le module Arduino avec l'outil de ligne de 
## commande Arduino.
##  

## COMMANDES
##  
## Afficher ce message d'aide
help:
	@awk '/^## / \
		        { if (c) {print c}; c=substr($$0, 4); next } \
		         c && /(^[[:alpha:]][[:alnum:]_-]+:)/ \
		        {print $$1, "\t", c; c=0} \
		         END { print c }' $(MAKEFILE_LIST)

## Raccourci francophone pour l'aide
aide: help

## Tout compiler et installer, puis rouler les tests. Un peu excessif.
all: install alldocs tests

## Raccourci francophone pour all
tout: all

## Installer tous les modules et la documentation
install: arduino python 

## Raccourci francophone pour install
installer: install

## Compiler tous les modules et la documentation
build: $(arduino_package) $(BUILD) alldocs

## Raccourci francophone pour build
batir: build

## Compiler et installer le module Arduino
arduino: $(arduino_package)
	$(arduino-cli) lib install --zip-path $<

$(arduino_package): $(arduino_fichiers) $(arduino_fichiers_source)
	$(tar) -r -u -f $@ $(arduino_fichiers)
	$(tar) -r -u -f $@/src $(arduino_fichiers_source)

$(arduino_fichiers):

## Compiler et installer le module Python
python: $(dir_source_python) $(pyproject) $(pip)
	$(pip) install --user .

## Créer un environnement virtuel pour le développement des modules
develop: $(python) $(pipenv) $(arduino-cli)
	$(pipenv) --python $(python_version)

## Compiler la documentation sous tous les formats
alldocs: pdfdocs htmldocs

## Raccourci francophone pour alldocs
tousdocs: alldocs

## Compiler la documentation au format PDF
pdfdocs:
	$(MAKE) -C $(dir_docs) latexpdf

## Compiler la documentation au format HTML
htmldocs:
	$(MAKE) -C $(dir_docs) singlehtml
	
## Compiler la documentation au format TeXinfo
texdocs:
	$(MAKE) -C $(dir_docs) texinfo
	
## Compiler la documentation au format man
mandocs:
	$(MAKE) -C $(dir_docs) man

## Publier le module Python et l'archive Arduino
publish publier:

$(python):
	@[[ -x $(python) ]] || echo "Vous devez installer Python $(python_version)."

pip: $(python) $(DIR_DRAPEAUX)/pip

$(DIR_DRAPEAUX)/pip: $(python) $(DIR_DRAPEAUX)
	$(python) -m ensurepip
	touch $(DIR_DRAPEAUX)/pip

pipenv: $(DIR_DRAPEAUX)/pipenv

$(DIR_DRAPEAUX)/pipenv: pip $(DIR_DRAPEAUX)
	$(pip) install pipenv

$(arduino-cli): $(dir_outils) $(curl)
	$(curl) -fsSL $(arduino-cli_url) | BINDIR=$(dir_outils) $(SHELL)

$(curl):
	@[[ -x $(curl) ]] || echo "Installez l'outil curl."
