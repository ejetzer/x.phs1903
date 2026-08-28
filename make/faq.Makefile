curr_mk := $(lastword $(MAKEFILE_LIST))
$(info Lecture de $(curr_mk)...)

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
github2rst = $(pipenv) run python $(lib_dir)/github/issues2rst.py
issues_rst = $(docs_src)/issues.rst

faq: $(logs)
	$(info Connecting to $(askbot_server)...)
	$(json2rst) >$(faq_rst) 2> "$(LOGS)/$(notdir $@).log"

issues: $(logs)
	$(info Connecting to GitHub...)
	$(github2rst) >$(issues_rst) 2> "$(LOGS)/$(notdir $@).log"

.PHONY: faq issues



$(info $(curr_mk) lu.)
