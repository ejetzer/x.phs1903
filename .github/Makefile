NAME = xphs1903
SHELL = /usr/bin/zsh
BUILD = ../.build

$(BUILD):
	mkdir -p $@

python: $(BUILD)
	# Build wheel & source distribution
	cd ..
	pipenv requirements --exclude-index --no-lock|sed 's/==/~=/g' > .github/$(BUILD)/requirements.txt
	pipenv run python -m build --sdist --outdir=.github/$(BUILD)
	pipenv run python -m build --wheel --outdir=.github/$(BUILD)

ARDUINO_SRC = ../src/arduino
ARDUINO_CFG = ../cfg

arduino: $(BUILD)
	# Build Arduino package
	mkdir -p $(BUILD)/$(NAME)/src
	cp -r $(ARDUINO_SRC)/*(.) $(BUILD)/$(NAME)/src/
	cp -r $(ARDUINO_SRC)/*(/) $(BUILD)/$(NAME)/
	cp -r $(ARDUINO_CFG)/keywords.txt $(ARDUINO_CFG)/library.* $(BUILD)/$(NAME)/
	cd $(BUILD) && (([[ -e $(NAME).zip ]] && $(tar) -u -f $(NAME).zip $(NAME)/*) || $(tar) -c -f $(NAME).zip $(NAME)/*)

pdf: $(BUILD)
	cp -r $(BUILD)/latex $(BUILD)/latexpdf
	-cd $(BUILD)/latexpdf && latexmk $(NAME).tex
