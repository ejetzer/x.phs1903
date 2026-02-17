# Installation de modules
arduino_proprietes = library.properties
dir_source_arduino = $(SOURCE)/arduino

arduino_exemples = examples
arduino_extras = extras
arduino_build = $(BUILD)
arduino_prebuild = $(arduino_build)/$(NAME)
arduino_package = $(arduino_build)/$(NAME).zip
arduino_fichiers = $(arduino_proprietes) $(arduino_extras) $(arduino_exemples)
arduino_fichiers_source = $(dir_source_arduino)/serveur $(dir_source_arduino)/onboard $(dir_source_arduino)/xphs1903.h
arduino_prebuild_fichiers = $(patsubst %,$(arduino_prebuild)/%,$(arduino_fichiers))
arduino_prebuild_fichiers_source = $(patsubst $(dir_source_arduino)/%,$(arduino_prebuild)/src/%,$(arduino_fichiers_source))
arduino_config = arduino.yaml

## Compiler et installer le module Arduino
arduino: $(arduino_package)
	$(arduino-cli) lib install --config-file $(arduino_config) --zip-path $<

$(arduino_package): $(arduino_prebuild_fichiers) $(arduino_prebuild_fichiers_source)
	cd $(arduino_build) && (([[ -e $(NAME).zip ]] && $(tar) -u -f $(NAME).zip $(NAME)/*) || $(tar) -c -f $(NAME).zip $(NAME)/*)

$(arduino_prebuild_fichiers): $(arduino_prebuild)/%: % $(arduino_prebuild)
	$(cp) -r $< $@

$(arduino_prebuild) $(arduino_prebuild)/src:
	$(mkdir) -p $@

$(arduino_prebuild_fichiers_source): $(arduino_prebuild)/src/%: $(dir_source_arduino)/% $(arduino_prebuild)/src
	$(cp) -r $< $@

$(arduino_fichiers):
	$(touch) $@