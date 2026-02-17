# Documentation
dir_docs = docs
docs_prerequis = $(dir_docs)/requirements.txt
dir_docs_source = $(dir_docs)/source
dir_docs_build = $(dir_docs)/_build
readthedocs = .readthedocs.yaml

## Compiler la documentation sous tous les formats
alldocs: pdfdocs htmldocs

## Raccourci francophone pour alldocs
tousdocs: alldocs

## Compiler la documentation au format PDF
pdfdocs:
	-$(MAKE) -C $(dir_docs) latexpdf

## Compiler la documentation au format HTML
htmldocs:
	$(MAKE) -C $(dir_docs) singlehtml
	
## Compiler la documentation au format TeXinfo
texdocs:
	$(MAKE) -C $(dir_docs) texinfo
	
## Compiler la documentation au format man
mandocs:
	$(MAKE) -C $(dir_docs) man
