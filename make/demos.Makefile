curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

demos = $(BUILD)/python-demo.zip $(BUILD)/arduino-demo.zip

demos: $(demos)

$(BUILD)/python-demo.zip: $(SOURCE)/xphs1903/demos
	( [[ -f $< ]] && tar -uf $@ $< ) || tar -cf $@ $<

$(BUILD)/arduino-demo.zip: $(SOURCE)/arduino/examples
	( [[ -f $< ]] && tar -uf $@ $< ) || tar -cf $@ $<

$(info $(curr_mk) lu.)
