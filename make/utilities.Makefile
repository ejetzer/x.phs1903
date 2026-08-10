# Programmes utilitaires
dir_outils ?= lib
python_version ?= 3.14
python ?= /usr/local/bin/python$(python_version)
pip ?= $(python) -m pip
pipenv ?= $(python) -m pipenv
arduino-cli ?= $(dir_outils)/arduino-cli
arduino-cli_url ?= https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh
curl ?= /usr/bin/curl
tar ?= /usr/bin/tar
touch ?= /usr/bin/touch
mkdir ?= /bin/mkdir
awk ?= /usr/bin/awk
rm ?= /bin/rm
cp ?= /bin/cp
git ?= /usr/bin/git

outils_externes = $(curl) $(tar) $(touch) $(mkdir) $(awk) $(rm) $(cp) $(python) $(git)

$(arduino-cli): $(dir_outils) $(curl)
	$(curl) -fsSL $(arduino-cli_url) | BINDIR=$(dir_outils) $(SHELL)

$(outils_externes):
	@[[ -x $@ ]] || echo "Installez l'outil $(shell basename $@) ou définissez la variable appropriée."

arduinoFFT = $(dir_outils)/arduinoFFT
arduinoFFT_prebuild = $(BUILD)
arduinoFFT_pkg = $(arduinoFFT_prebuild)/arduinoFFT.zip
arduino_config ?= $(CONFIG)/arduino.yaml
$(arduinoFFT): $(git)
	$(git) submodule init && $(git) submodule update 2> "$(LOGS)/$(notdir $@).log"

$(arduinoFFT_pkg): $(arduinoFFT_prebuild) $(arduinoFFT) $(tar) $(cp) $(rm)
	$(rm) -rf $@ || echo 'Rien à effacer pour' $@
	$(cp) -r $(arduinoFFT) $(arduinoFFT_prebuild)
	{cd $(arduinoFFT_prebuild) && (([[ -e arduinoFFT.zip ]] && $(tar) -u -f arduinoFFT.zip arduinoFFT/*) || $(tar) -c -f arduinoFFT.zip arduinoFFT/*)} 2> "$(LOGS)/$(notdir $@).log"

arduinoFFT: $(arduinoFFT_pkg) $(arduino-cli)
	$(arduino-cli) lib install --config-file $(arduino_config) --zip-path $< 2> "$(LOGS)/$(notdir $@).log"

arduinoSTL = $(dir_outils)/ArduinoSTL
arduinoSTL_prebuild = $(BUILD)
arduinoSTL_pkg = $(arduinoSTL_prebuild)/ArduinoSTL.zip
$(arduinoSTL): $(git)
	$(git) submodule init && $(git) submodule update

$(arduinoSTL_pkg): $(arduinoSTL_prebuild) $(arduinoSTL) $(tar) $(cp) $(rm)
	$(rm) -rf $@ || echo 'Rien à effacer pour' $@
	$(cp) -r $(arduinoSTL) $(arduinoSTL_prebuild)
	{cd $(arduinoSTL_prebuild) && (([[ -e arduinoSTL.zip ]] && $(tar) -u -f arduinoSTL.zip arduinoSTL/*) || $(tar) -c -f arduinoSTL.zip arduinoSTL/*)} 2> "$(LOGS)/$(notdir $@).log"

arduinoSTL: $(arduinoSTL_pkg) $(arduino-cli)
	$(arduino-cli) lib install --config-file $(arduino_config) --zip-path $< 2> "$(LOGS)/$(notdir $@).log"
