curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

## COMMANDES
##  
## Afficher ce message d'aide
help:
	@$(awk) '/^## / \
		        { if (c) {print c}; c=substr($$0, 4); next } \
		         c && /(^[[:alpha:]][[:alnum:]_-]+:)/ \
		        {print $$1, "\t", c; c=0} \
		         END { print c }' $(MAKEFILE_LIST)


$(info $(curr_mk) lu.)
