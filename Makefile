#/***************************************************************************
# AzureMapsPlugin
#
# Azure Maps plugin for QGIS 3
#							 -------------------
#		begin				: 2019-06-04
#		git sha				: $Format:%H$
#		copyright			: (C) 2019 by Microsoft Corporation
#		email				: japark@microsoft.com, xubin.zhuge@microsoft.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################

# QGISDIR points to the location where your plugin should be installed.
# This varies by platform, relative to your HOME directory:
#	* Linux:
#	  .local/share/QGIS/QGIS3/profiles/default/python/plugins/
#	* Mac OS X:
#	  Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
#	* Windows:
#	  AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins'

HOME=C:\Users\enterYourUserNameHere
QGISDIR=AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins

#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES =

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
#LRELEASE = lrelease
#LRELEASE = lrelease-qt4

# translation
SOURCES = \
	__init__.py \
	azure_maps_plugin.py azure_maps_plugin_dialog.py

PLUGINNAME = QGISPlugin

PY_FILES = \
	__init__.py \
	azure_maps_plugin.py azure_maps_plugin_dialog.py \
	azure_maps_plugin_floor_picker.py azure_maps_plugin_welcome_message.py \

UI_FILES = azure_maps_plugin_dialog_base.ui azure_maps_plugin_floor_picker.ui azure_maps_plugin_welcome_message.ui

EXTRAS = metadata.txt plugin-config.ini

MEDIA = media

EXTRA_DIRS = geojson models defs helpers

COMPILED_RESOURCE_FILES = resources.py

PEP8EXCLUDE=pydev,resources.py,conf.py,third_party,ui

#################################################
# Normally you would not need to edit below here
#################################################

HELP = help\build\html

PLUGIN_UPLOAD = $(c)/plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

win-compile:
	.\src\build\compile.bat

win-deploy: win-compile win-doc
	@echo ------------------------------------------
	@echo The win-deploy target only works on Windows operating system where the Python plugin directory is located at:
	@echo $(HOME)\$(QGISDIR)
	@echo ------------------------------------------
	@echo Deploying plugin to your QGIS Plugin directory.
	@echo ------------------------------------------
	FOR %%f in ($(HELP)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME)\help /y /i
	FOR %%f in ($(PY_FILES)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME) /y /i
	FOR %%f in ($(UI_FILES)) DO xcopy .\src\ui\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME) /y /i
	FOR %%f in ($(COMPILED_RESOURCE_FILES)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME) /y /i
	FOR %%f in ($(MEDIA)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME)\$(MEDIA) /y /i
	FOR %%f in ($(EXTRAS)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME) /y /i
	FOR %%f in ($(EXTRA_DIRS)) DO xcopy .\src\%%f $(HOME)\$(QGISDIR)\$(PLUGINNAME)\%%f /y /i /E

win-delete:
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rd /S /Q $(HOME)\$(QGISDIR)\$(PLUGINNAME)

win-clean:
	@echo "-----------------------------------"
	@echo "Removing files not tracked by git."
	@echo "-----------------------------------"
	git clean -x -f

win-doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd .\src\help & make html

########################################################################################################################################################
# This project was initially created using a unix system, so please be aware that the make targets below are designed for unix and do no support windows.
########################################################################################################################################################

.PHONY: default
default:
	@echo While you can use make to build and deploy your plugin, pb_tool
	@echo is a much better solution.
	@echo A Python script, pb_tool provides platform independent management of
	@echo your plugins and runs anywhere.
	@echo You can install pb_tool using: pip install pb_tool
	@echo See https://g-sherman.github.io/plugin_build_tool/ for info. 

unix-compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $<

%.qm : %.ts
	$(LRELEASE) $<

test: unix-compile transcompile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		nosetests -v --with-id --with-coverage --cover-package=. \
		3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

unix-deploy: unix-compile doc transcompile
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis2 directory."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vfr i18n $(HOME)/$(QGISDIR)/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/$(QGISDIR)/$(PLUGINNAME)/help
	# Copy extra directories if any
	(foreach EXTRA_DIR,(EXTRA_DIRS), cp -R (EXTRA_DIR) (HOME)/(QGISDIR)/python/plugins/(PLUGINNAME)/;)

# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
unix-clean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


unix-delete:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/$(PLUGINNAME)

zip: unix-deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

package: unix-compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES)

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	@chmod +x scripts/compile-strings.sh
	@scripts/compile-strings.sh $(LRELEASE) $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

doc:
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	cd help; make html

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude $(PEP8EXCLUDE) . || true
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)
