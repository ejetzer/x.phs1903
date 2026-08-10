curl ?= /usr/bin/curl
jq ?= /usr/bin/jq
askbot_server = http://localhost:8000
askbot_api_url = $(askbot_server)/api/v1/questions/
docs_dir = docs
docs_src = $(docs_dir)/src
faq_json = $(docs_src)/faq.json
faq_rst = $(docs_src)/faq.rst
lib_dir ?= lib
json2rst = $(pipenv) run python $(lib_dir)/askbot/json2rst.py

faq: $(logs)
	$(info Connecting to $(askbot_server)...)
	$(json2rst) >$(faq_rst) || $(warning Could not connect.) 2> "$(LOGS)/$(notdir $@).log"

.PHONY: faq

