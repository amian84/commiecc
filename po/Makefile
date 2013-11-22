#!/usr/bin/make -f

PROJECT = commiecc

GETTEXT = /usr/bin/xgettext
MSGMERGE = /usr/bin/msgmerge

PO = $(shell find . -name *.po -print | sed -e 's!./!!g')

update-po:
	$(GETTEXT) -f POTFILES -d $(PROJECT) -o $(PROJECT).pot --language=python
	$(GETTEXT) -f POTFILES -d $(PROJECT) -o $(PROJECT).pot -j
	$(GETTEXT) -f POTFILESUI -d $(PROJECT) -o $(PROJECT).pot -j --language=glade
	for lang in $(PO); do $(MSGMERGE) -U $$lang $(PROJECT).pot; done 
