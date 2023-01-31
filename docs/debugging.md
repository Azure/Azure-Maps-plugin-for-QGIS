# Debugging Guidelines


## Debug with Visual Studio Code
Check the file [Debugger-VSCode](./debugger-vscode.md) to learn how to debug with Visual Studio Code


## Debugging with other Editors
For other IDEs, please check this link [QGIS IDE Debugging](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/plugins/ide_debugging.html)


## General Guidelines
- Bottom right corner of QGIS has a message icon, which opens up the logs for plugin. Brief explainations of the windows is given here: 
    - *Python warnings:* By QGIS. Warnings/Errors for Python in QGIS (eg compile errors).
    - *Plugins:* By QGIS. Logger for the plugin (eg Plugin loaded etc).
    - *General:* By QGIS. Ignore, general QGIS errors.
    - *Logs:* From Plugin. Plugin related logging messages, consisting of requests made by the plugin on user's behalf. 

TODO: Move *Messages* and *Patch Request* under one log.

TODO: Add more logging.


## Logging 
To log in QGIS, you can use the following code
```python
QgsMessageLog.logMessage(
    <Error Message HERE>, <Window name/TAG for error message>, <Severity based on Message Levels (check below)>
)
```
Follow the guide [here](https://qgis.org/pyqgis/3.2/core/Message/QgsMessageLog.html#qgis.core.QgsMessageLog.logMessage) for more information

For message levels, check [this](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/communicating.html#id6) and search for *MessageLevels*