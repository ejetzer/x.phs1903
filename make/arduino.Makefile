# Installation de modules
arduino_proprietes = $(CONFIG)/library.properties $(CONFIG)/library.json
arduino_fichiers := $(shell echo $(SOURCE)/arduino/**/*(.))
arduino_dirs := $(shell echo $(SOURCE)/arduino/**/*(/))
arduino_target_dirs := $(patsubst $(SOURCE)/arduino/%,$(BUILD)/$(NAME)/%,$(arduino_dirs))
arduino_targets := $(patsubst $(SOURCE)/arduino/%,$(BUILD)/$(NAME)/%,$(arduino_fichiers))
arduino_targets_cfg := $(patsubst $(CONFIG)/%,$(BUILD)/$(NAME)/%,$(arduino_proprietes))
arduino_cli ?= /usr/local/bin/arduino-cli

arduino: $(BUILD)/$(NAME).zip

$(BUILD)/$(NAME).zip: $(arduino_targets) $(arduino_targets_cfg)
	{cd $(BUILD) && ( ( [[ -e $(NAME).zip ]] && $(tar) -uf $(NAME).zip $(NAME)/* ) || $(tar) -cf $(NAME).zip $(NAME)/* )} 2> "$(LOGS)/$(notdir $@).log"

$(BUILD)/$(NAME) $(arduino_target_dirs):
	$(mkdir) -p $@

$(arduino_targets): $(BUILD)/$(NAME)/%: $(SOURCE)/arduino/% $(arduino_target_dirs)
	$(cp) $< $@

$(arduino_targets_cfg): $(BUILD)/$(NAME)/%: $(CONFIG)/% $(BUILD)/$(NAME)
	$(cp) $< $@

arduino-install: $(BUILD)/$(NAME).zip arduino arduinoFFT arduinoSTL
	$(arduino-cli) lib install --config-file $(arduino_config) --zip-path $< 2> "$(LOGS)/$(notdir $@).log"
