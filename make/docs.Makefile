curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

# Documentation
dir_docs = docs
dir_docs_source = $(dir_docs)/src
prerequis_docs ?= $(BUILD)/requirements.txt

SPHINXOPTS    ?= -v
SPHINXBUILD   ?= $(pipenv) run sphinx-build
SOURCEDIR     = docs/src
BUILDDIR      = $(BUILD)

conf_py = $(SOURCEDIR)/conf.py
docs_prereqs = $(BUILD)/requirements.txt
dir_docs_build = $(BUILD)
readthedocs = .readthedocs.yaml

html_dir ?= $(BUILD)/singlehtml
html_names ?= index.html objects.inv _downloads _static
html_files ?= $(addprefix $(html_dir)/,$(html_names))

helpdocs:
	$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) 2> "$(LOGS)/$(notdir $@).log"

cleandocs:
	$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) 2> "$(LOGS)/$(notdir $@).log"

## Compiler la documentation sous tous les formats
alldocs: pdfdocs htmldocs texdocs mandocs

## Raccourci francophone pour alldocs
tousdocs: alldocs

## Compiler la documentation au format PDF
pdfdocs latexpdf: $(BUILD)/$(NAME).pdf

$(BUILD)/latex/$(NAME).tex: $(prerequis_docs) $(conf_py)
	$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(0) 2> "$(LOGS)/$(notdir $@).log"

$(BUILD)/latex/%.pdf: $(BUILD)/latex/%.tex
	cd $(BUILDDIR)/latex && latexmk

$(BUILD)/%.pdf: $(BUILD)/latex/%.pdf
	cp -rf $< $(dir $@)

## Compiler la documentation au format HTML
htmldocs singlehtml: $(html_files)

$(html_files): $(prerequis_docs) $(conf_py)
	$(SPHINXBUILD) -M singlehtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) 2> "$(LOGS)/$(notdir $@).log"

## Compiler la documentation au format TeXinfo
texdocs: texinfo

## Compiler la documentation au format man
mandocs: man

man texinfo: $(prerequis_docs) $(conf_py)
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) 2> "$(LOGS)/$(notdir $@).log"

# Figures TikZ

FIGS = $(SOURCEDIR)/tuto/acq/multiblink.png $(SOURCEDIR)/tuto/acq/oscilloscope.png
SVGS = $(patsubst %.png,%.svg,$(FIGS))
PDFS = $(patsubst %.png,%.pdf,$(FIGS))
TIKZ = $(patsubst %.png,%.tikz,$(FIGS))
$(info Fichiers TikZ)
$(info )
$(info --------------)
$(info )
$(info $(TIKZ))
$(info )
$(info Fichiers PDF)
$(info )
$(info --------------)
$(info )
$(info $(PDFS))
$(info )
$(info Fichiers PNG)
$(info --------------)
$(info )
$(info $(FIGS))
$(info )

$(TIKZ):
	[[ -e $@ ]]

latexmkrc = docs/src/latexmkrc
latexmk = /Library/TeX/texbin/latexmk
$(PDFS): %.pdf: %.tikz
	$(latexmk) -gg -norc -r $(latexmkrc) -out2dir="$(dir $@)" $< 2> "$(LOGS)/$(notdir $@).log"

MAGICK = /Users/emilejetzer/.local/bin/magick
$(FIGS): %.png: %.pdf
	$(MAGICK) -density 600 $< $@ 2> "$(LOGS)/$(notdir $@).log"

$(SVGS): %.svg: %.pdf
	$(MAGICK) $< $@ 2> "$(LOGS)/$(notdir $@).log"

figures: $(FIGS) #$(SVGS)

$(info $(curr_mk) lu.)
