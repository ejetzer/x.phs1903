demos = $(BUILD)/python-demo.zip $(BUILD)/arduino-demo.zip

$(BUILD)/python-demo.zip: $(SOURCE)/xphs1903/demos
	( [[ -f $< ]] && tar -uf $@ $< ) || tar -cf $@ $<

$(BUILD)/arduino-demo.zip: $(SOURCE)/arduino/examples
	( [[ -f $< ]] && tar -uf $@ $< ) || tar -cf $@ $<