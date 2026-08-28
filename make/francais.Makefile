curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

tout: all
installer: install
batir: build
nettoyer: clean
docu: alldocs
publier: publish
aide: help
	
.PHONY: tout installer batir nettoyer docu publier aide


$(info $(curr_mk) lu.)
