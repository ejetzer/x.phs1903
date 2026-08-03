NAME = xphs1903
SHELL = /usr/bin/zsh
VERSION = $(shell git describe --always)
BUILD = .build

ARDUINO_SRC = ../src/arduino
ARDUINO_CFG = ../cfg

arduino: $(BUILD)
	# Build Arduino package
	mkdir -p $(BUILD)/$(NAME)/src
	cp -r $(ARDUINO_SRC)/*(.) $(BUILD)/$(NAME)/src/
	cp -r $(ARDUINO_SRC)/*(/) $(BUILD)/$(NAME)/
	cp -r $(ARDUINO_CFG)/keywords.txt $(ARDUINO_CFG)/library.* $(BUILD)/$(NAME)/
	cd $(BUILD) && (([[ -e $(NAME).zip ]] && $(tar) -u -f $(NAME).zip $(NAME)/*) || $(tar) -c -f $(NAME).zip $(NAME)/*)

