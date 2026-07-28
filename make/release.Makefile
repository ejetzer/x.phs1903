VERSION ?= $(shell git describe --always)
release_name ?= $(NAME)_$(VERSION)
release_dir ?= $(BUILD)/$(release_name)

$(release_dir):
	mkdir -p $@

release: $(release_dir).zip

$(release_dir).zip: htmldocs pdfdocs sdist wheel $(BUILD)/xphs1903.zip $(BUILD)/template.zip $(release_dir)
	cp $(BUILD)/template.zip $(release_dir)
	cp $(BUILD)/xphs1903.zip $(release_dir)
	cp $(BUILD)/wheel/*.whl $(release_dir)
	cp $(BUILD)/sdist/*.tar.gz $(release_dir)
	cp $(BUILD)/latex/*.pdf $(release_dir)
	cp -r $(BUILD)/singlehtml/* $(release_dir)
	cd $(BUILD) && ( ( [[ -e $(release_name).zip ]] && $(tar) -uf $(release_name).zip $(release_name)/* ) || $(tar) -cf $(release_name).zip $(release_name)/* )

share export: $(release_name).zip

$(release_name).zip: release
	cp $(release_dir).zip .
