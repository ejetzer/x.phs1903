SHELL = /usr/bin/zsh
GITHUB_BUILD = .build

$(GITHUB_BUILD):
	mkdir -p $@

github-build: $(GITHUB_BUILD)
	# Build wheel & source distribution
	pipenv requirements --exclude-index --no-lock|sed 's/==/~=/g' > $(GITHUB_BUILD)/requirements.txt
	pipenv run python -m build --wheel --sdist --outdir=$(GITHUB_BUILD)
	# Build Arduino package
	mkdir -p $(GITHUB_BUILD)/$(NAME)/src
	cp -r $(dir_source_arduino)/*(.) $(GITHUB_BUILD)/$(NAME)/src/
	cp -r $(dir_source_arduino)/*(/) $(GITHUB_BUILD)/$(NAME)/
	cp -r $(dir_config_arduino)/keywords.txt $(dir_config_arduino)/library.* $(GITHUB_BUILD)/$(NAME)/
	cd $(GITHUB_BUILD) && (([[ -e $(NAME).zip ]] && $(tar) -u -f $(NAME).zip $(NAME)/*) || $(tar) -c -f $(NAME).zip $(NAME)/*)
	# Build documentation as pdf
	@pipenv run sphinx-build -M latex docs/src "$(GITHUB_BUILD)" $(SPHINXOPTS) $(O)
	cp -r $(GITHUB_BUILD)/latex $(GITHUB_BUILD)/latexpdf
	cd $(GITHUB_BUILD)/latexpdf && latexmk $(NAME).tex
