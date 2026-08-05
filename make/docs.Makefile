# Documentation
dir_docs = docs
dir_docs_source = $(dir_docs)/src
prerequis_docs ?= docs/src/requirements.txt

SPHINXOPTS    ?= -v
SPHINXBUILD   ?= $(pipenv) run sphinx-build
SOURCEDIR     = docs/src
BUILDDIR      = $(BUILD)

docs_prereqs = $(dir_docs_source)/requirements.txt
dir_docs_build = $(BUILD)
readthedocs = .readthedocs.yaml


helpdocs:
	$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

cleandocs:
	$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

## Compiler la documentation sous tous les formats
alldocs: pdfdocs htmldocs texdocs mandocs

## Raccourci francophone pour alldocs
tousdocs: alldocs

## Compiler la documentation au format PDF
pdfdocs latexpdf: $(prerequis_docs)
	$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(0)
	cd $(BUILDDIR)/latex && latexmk

## Compiler la documentation au format HTML
htmldocs: singlehtml

## Compiler la documentation au format TeXinfo
texdocs: texinfo

## Compiler la documentation au format man
mandocs: man

singlehtml man texinfo: $(prerequis_docs)
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
