build: .build/xphs1903.zip

help:
	@echo "Fichier de compilation de module Arduino"

.build:
	mkdir -p $@

.build/arduino: .build
	mkdir -p $@

.build/arduino/src .build/arduino/examples: .build/arduino
	mkdir -p $@

.build/arduino/src/xphs1903.h: .build/arduino/src/%: src/arduino/% .build/arduino/src
	cp $< $@
	
.build/arduino/examples/freq_adc .build/arduino/examples/annonceur: .build/arduino/examples/%: tests/% .build/arduino/examples
	cp -r $< $@

.build/arduino/arduino.yaml .build/arduino/keywords.txt .build/arduino/library.properties: .build/arduino/%: % .build
	cp $< $@

clean:
	-rm -rf .build/arduino

wipe:
	-rm -rf .build/arduino
	-rm -rf .build/xphs1903.zip

.build/xphs1903.zip: .build/arduino/src/xphs1903.h .build/arduino/examples/freq_adc .build/arduino/examples/annonceur .build/arduino/arduino.yaml .build/arduino/keywords.txt .build/arduino/library.properties
	cp -r .build/arduino/ .build/xphs1903/
	[[ -e $@ ]] && tar -uf $@ -C .build/ xphs1903/ || tar -cf $@ -C .build/ xphs1903/
	rm -rf .build/xphs1903/

