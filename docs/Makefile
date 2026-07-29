# Minimal makefile for Sphinx documentation
#

DIR_DRAPEAUX = ../.drapeaux

prerequis = "src/requirements.txt"

include ../make/utilities.Makefile
include ../make/pipenv.Makefile

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -v
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = src
BUILDDIR      = ../.build

# Put it first so that "make" without argument is like "make help".
help:
	@$(pipenv) run $(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@$(pipenv) run $(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

all: singlehtml man latexpdf texinfo

.PHONY: help Makefile $(DIR_DRAPEAUX) init clean all

$(DIR_DRAPEAUX):
	$(mkdir) -p $@

init: Pipfile.lock

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
singlehtml man texinfo: Makefile init $(prerequis)
	@$(pipenv) run $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

latexpdf: Makefile init $(prerequis)
	$(pipenv) run $(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(0)
	cd $(BUILDDIR)/latex && latexmk
