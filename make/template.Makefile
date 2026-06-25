template_dir ?= template
template_build ?= $(BUILD)/template
template_files ?= $(wildcard $(template_dir)/*)
template_build_files ?= $(patsubst $(template_dir)/%,$(template_build)/%, $(template_files))
template_archive ?= $(BUILD)/template.zip

.PHONY: modele

modele: $(template_archive)

$(template_archive): $(template_build_files)
	cd $(BUILD) && ( ( [[ -e template.zip ]] && $(tar) -uf template.zip template/* ) || $(tar) -cf template.zip template/* )

$(template_build_files): $(template_build)/%: $(template_dir)/% $(template_build)
	-rm -rf $@
	cp -r $< $@

$(template_build): $(BUILD)
	mkdir -p $@
