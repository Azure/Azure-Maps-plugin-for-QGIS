# Debugging Guidelines


## Debug with Visual Studio Code
Check the file [Debugger-VSCode](./debugger-vscode.md) to learn how to debug with Visual Studio Code

## Debugging with other Editors
For other IDEs, please check this link [QGIS IDE Debugging](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/plugins/ide_debugging.html)

## Use Test Environment
- Search for `atlas.microsoft.com` in the file [azure_maps_plugin.py](../src/azure_maps_plugin.py). Add respective code to add test environment.
- Add Test enivronment option in the file [azure_maps_plugin_dialog_base](../src/ui/azure_maps_plugin_dialog_base.ui)
    - Under `<widget class="QComboBox" name="geographyDropdown">`, add the following

    ```xml
    <item>
        <property name="text">
        <string>Test</string>
        </property>
    </item>
    ```

## Build Errors
- In case you get an error similar to `'sphinx-build' is not recognized as an internal or external command`, you might have to install [sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html) using `choco install sphinx`.

### Clear Cache
Sometimes, QGIS plugin won't load the changes made. This happens espcially if you rename files/delete files, since that might not get propogated to the plugins folder when the plugin is built (changes in a file are overriden). In this scenario, you can manually flush the cache/old plugin folder.
- Identify where your plugin is compiled. For windows, it should be at `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISPlugin`, as defined in the makefile
- You can delete specific files or the entire `QGISPlugin` folder
- Reload the plugin in QGIS using plugin reloader, to ensure changes are put in effect.