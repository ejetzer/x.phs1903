# Programmes utilitaires
dir_outils ?= outils
python_version ?= 3.14
python ?= /usr/local/bin/python3.14
pip ?= $(python) -m pip
pipenv ?= $(python) -m pipenv
arduino-cli ?= $(dir_outils)/arduino-cli
arduino-cli_url = https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh
curl ?= /usr/bin/curl
tar ?= /usr/bin/tar
touch ?= /usr/bin/touch
mkdir ?= /bin/mkdir
awk ?= /usr/bin/awk
rm ?= /bin/rm
cp ?= /bin/cp

outils_externes = $(curl) $(tar) $(touch) $(mkdir) $(awk) $(rm) $(cp) $(python)

# ---

$(arduino-cli): $(dir_outils) $(curl)
	$(curl) -fsSL $(arduino-cli_url) | BINDIR=$(dir_outils) $(SHELL)

$(outils_externes):
	@[[ -x $@ ]] || echo "Installez l'outil $(shell basename $@)."

