VERSION ?= $(shell git describe --always)
release_name ?= $(NAME)_$(VERSION)
release_dir ?= $(BUILD)/$(release_name)
release_template ?= $(release_dir)/template.zip
release_arduino ?= $(release_dir)/$(NAME).zip

sdist_name ?= x_phs1903-$(VERSION).tar.gz
wheel_name ?= x_phs1903-$(VERSION)-py3-none-any.whl
release_wheel ?= $(addprefix $(release_dir)/,$(wheel_name))
release_sdist ?= $(addprefix $(release_dir)/,$(sdist_name))

release_latex ?= $(release_dir)/$(NAME).pdf

html_dir = $(BUILD)/singlehtml
html_names = index.html objects.inv _downloads _static
html_files = $(addprefix $(html_dir)/,$(html_names))
release_singlehtml ?= $(patsubst $(BUILD)/%,$(release_dir)/%,$(html_files))

release_files = $(release_arduino) $(release_template) $(release_wheel) $(release_sdist) $(release_latex) $(release_singlehtml)

$(release_dir) $(release_dir)/singlehtml:
	mkdir -p $@

release build: upverse $(release_dir).zip

$(release_dir).zip: $(release_files)
	{cd $(BUILD) && ( ( [[ -e $(release_name).zip ]] && $(tar) -uf $(release_name).zip $(release_name)/* ) || $(tar) -cf $(release_name).zip $(release_name)/* )} 2> "$(LOGS)/$(notdir $@).log"

$(release_files): $(release_dir)/%: $(BUILD)/% $(release_dir)
	cp -rf $< $(release_dir)/

$(BUILD)/$(wheel_name): $(wheel)/$(wheel_name)
	cp $< $(BUILD)/

$(BUILD)/$(sdist_name): $(sdist)/$(sdist_name)
	cp $< $(BUILD)/

share export: $(release_name).zip

$(release_name).zip: release
	cp $(release_dir).zip ./
