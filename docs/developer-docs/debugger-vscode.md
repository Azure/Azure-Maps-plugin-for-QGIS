# VS-Code Debugger Installation
Attach a debugger to VS-Code for QGIS.


## Requirements
1. QGIS
2. Python
3. Steps in the README.md


## Steps
1. Install [DebugVS plugin](https://plugins.qgis.org/plugins/debug_vs/) on QGIS.
    1. Go to Plugin > Manage and Install Plugin in QGIS.
    2. Search for and Install Debugvs plugin.
2. Install ptvsd in qgis python environment
    1. Navigate to `C:\Program Files\<QGIS Version folder>` (for instance `C:\Program Files\QGIS 3.22.5`).
    2. Open the OSGeo4W shell by running `OSGeo4W.bat`.
    3. Run `pip install ptvsd`.
        - If pip doesn't exist, follow the instructions [here](https://pip.pypa.io/en/stable/installation/#get-pip-py) to install pip on the QGIS environment.


## Debug
- On QGIS: Navigate to Plugins > Enable Debug for Visual Studio > Enable Debug for Visual Studio.
    - If you don't see this option, check if you have completed all steps above
- On VS-Code: Click Run > Start Debugging.
The debugger is now on. You can place breakpoints in vs-code to start!


## Errors
If there are any errors in debugging, check here:
- Check the [launch.json](../.vscode/launch.json) file.
    1. If port *5678* is used, change to different one and try compiling again.
    2. Check that local root points to the folder containing in the repo containing the plugin code.
    3. Check that remoteRoot points to the QGIS plugin folder. 
    If such folder doesn't exist, or if there is no plugin there, follow the steps here [remoteRoot setup QGIS plugin VS-Code Debugger](https://gispofinland.medium.com/cooking-with-gispo-qgis-plugin-development-in-vs-code-19f95efb1977#:~:text=Deploying%20the%20plugin).


## References
[A tutorial for QGIS Plugin Development in VS Code](https://gispofinland.medium.com/cooking-with-gispo-qgis-plugin-development-in-vs-code-19f95efb1977).