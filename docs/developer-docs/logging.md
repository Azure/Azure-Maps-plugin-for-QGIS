# Logging in Azure Maps QGIS Plugin

## View logs in QGIS
- Bottom right corner of QGIS has a message icon, which opens up the logs for plugin. Brief explainations of the windows is given here: 
    - *Python warnings:* By QGIS. Warnings/Errors for Python in QGIS (eg compile errors).
    - *Plugins:* By QGIS. Logger for the plugin (eg Plugin loaded etc).
    - *General:* By QGIS. Ignore, general QGIS errors.
    - *Logs:* From Plugin. Plugin related logging messages, consisting of requests made by the plugin on user's behalf. 

## AzureMapsPluginLogger
[AzureMapsPluginLogger.py](../src/helpers/AzureMapsPluginLogger.py) handles all logging for the plugin

### QGIS Logging
Logging in QGIS is handled by [QgsMessageLog](https://qgis.org/pyqgis/3.2/core/Message/QgsMessageLog.html) class. <br/>
It also has the following [message levels](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/communicating.html#id6)
- Info = 0
- Warning = 1
- Critical = 2
- Success = 3

### AzureMapsPluginLogger
AzureMapsPluginLogger is a custom class which uses QgsMessageLog. It has methods for logging at the above levels and to write logs to files as well. <br/>
It also stores the logs of failed requests & responses in a json. <br/>
Logs that are printed in QGIS (under the Logs tab) are the same as the ones written to files

### Debug Logs
Debug logs can be written in the code using `logger.QLogDebug` method. <br/>
To view debug logs, first set `debugLog=True` in `_create_helpers` function in [azure_maps_plugin.py](../../src/azure_maps_plugin.py). 
Only then will debug logs be displayed and printed.