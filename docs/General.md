# General
General documentation/comments to run the plugin

## Debug with Visual Studio Code
Check the file [Debugger-VSCode](./debugger-vscode.md) for more information

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
