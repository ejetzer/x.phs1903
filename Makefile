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
VERSION = $(shell git describe --always)
AUTHOR ?= "Émile Jetzer" "Jacques Massicotte"
SHELL = /bin/zsh
SOURCE ?= src
README ?= README.rst
BUILD ?= .build
CONFIG ?= cfg
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
##

# Pour les fichiers d'état
DIR_DRAPEAUX ?= .drapeaux

include make/utilities.Makefile
include make/pipenv.Makefile

# Raccourcis pratiques
dirs = $(DIR_DRAPEAUX) $(dir_docs_build) $(dir_outils) $(BUILD)\
	$(arduino_prebuild) $(arduino_prebuild)/src

## INSTALLATION
##
## L'installation des modules se fait avec les gestionnaires de paquet
## par défaut pour les environnements correspondants. Le module Python
## s'installe avec pip, et le module Arduino avec l'outil de ligne de
## commande Arduino.
##

include make/help.Makefile

.PHONY: help all install arduino python develop alldocs\
	pdfdocs htmldocs publish build clean

# Les répertoires d'installation ne faisant pas partie du répertoire
# git doivent pouvoir être créés sur le vif
$(dirs):
	$(mkdir) -p $@

include make/arduino.Makefile
include make/python.Makefile
include make/docs.Makefile
include make/tests.Makefile
include make/template.Makefile

init: Pipfile.lock $(MAKE)
	$(MAKE) -C $(dir_docs) init
	$(git) config include.path cfg/gitconfig

## Tout compiler et installer, puis rouler les tests. Un peu excessif.
all: install alldocs tests

clean:
	-$(rm) -rf $(BUILD)/* $(DIR_DRAPEAUX)/*
	$(MAKE) -C $(dir_docs) clean

## Installer tous les modules et la documentation
install: arduino python alldocs

## Compiler tous les modules et la documentation
build: develop $(arduino_package) $(sdist) $(wheel) alldocs $(demos)

## Créer un environnement virtuel pour le développement des modules
develop: pipenv $(arduino-cli)

## Publier le module Python et l'archive Arduino
twine = $(pipenv) run python -m twine
publish: $(sdist) $(wheel)
	$(twine) upload --verbose $(sdist)/* $(wheel)/*

include make/demos.Makefile

github-build:
	$(MAKE) -C .github/ build

include make/release.Makefile
include make/faq.Makefile
