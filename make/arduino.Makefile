# Installation de modules
dir_config_arduino ?= $(CONFIG)
arduino_proprietes ?= $(dir_config_arduino)/library.properties
arduino_json ?= $(dir_config_arduino)/library.json
dir_source_arduino ?= $(SOURCE)/arduino

arduino_exemples ?= $(dir_source_arduino)/examples
arduino_extras ?= $(dir_source_arduino)/extras
arduino_build ?= $(BUILD)
arduino_prebuild ?= $(arduino_build)/$(NAME)
arduino_package ?= $(arduino_build)/$(NAME).zip
arduino_fichiers ?= $(arduino_extras) $(arduino_exemples)
arduino_fichiers_config ?= $(arduino_proprietes) $(arduino_json)
arduino_fichiers_source ?= $(dir_source_arduino)/xphs1903.h $(dir_source_arduino)/adc1903.h $(dir_source_arduino)/fft1903.h $(arduino_fichiers)
arduino_prebuild_fichiers ?= $(patsubst %,$(arduino_prebuild)/%,$(arduino_fichiers))
arduino_prebuild_fichiers_source ?= $(patsubst $(dir_source_arduino)/%,$(arduino_prebuild)/src/%,$(arduino_fichiers_source))
arduino_prebuild_fichiers_config ?= $(patsubst $(dir_config_arduino)/%,$(arduino_prebuild)/%,$(arduino_fichiers_config))
arduino_config ?= $(CONFIG)/arduino.yaml

## Compiler et installer le module Arduino
arduino: $(arduino_package) arduinoFFT
	$(arduino-cli) lib install --config-file $(arduino_config) --zip-path $<

$(arduino_package): $(arduino_prebuild_fichiers_source) $(arduino_prebuild_fichiers_config)
	cd $(arduino_build) && (([[ -e $(NAME).zip ]] && $(tar) -u -f $(NAME).zip $(NAME)/*) || $(tar) -c -f $(NAME).zip $(NAME)/*)

#$(arduino_prebuild_fichiers): $(arduino_prebuild)/%: % $(arduino_prebuild)
#	$(cp) -r $< $@

$(arduino_prebuild) $(arduino_prebuild)/src:
	$(mkdir) -p $@

$(arduino_prebuild_fichiers_source): $(arduino_prebuild)/src/%: $(dir_source_arduino)/% $(arduino_prebuild)/src
	$(cp) -r $< $@

$(arduino_prebuild_fichiers_config): $(arduino_prebuild)/%: $(dir_config_arduino)/% $(arduino_prebuild)
	$(cp) -r $< $@

$(arduino_fichiers):
	$(touch) $@