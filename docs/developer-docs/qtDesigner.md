# QTDesigner
QGIS uses .UI files to design the ui. These UI files can be opened with QTDesigner

## Download and Install
Standalone QTDesigner can be install here [QTDesigner Download](https://build-system.fman.io/qt-designer-download). This link should be a third-party, however. If you want to get QTDesigner from the main source, you would have to downoad [Download QT](https://www.qt.io/download) and follow this guide [here](https://stackoverflow.com/questions/30222572/how-to-install-qtdesigner) to install designer (which comes as part of QT)
[Docs for QT Installation](https://docs.qgis.org/3.22/en/docs/developers_guide/qtcreator.html)

## Using QTDesigner

### UI Files
The plugin defines three ui files:
- [azure_maps_plugin_dialog_base.ui](../../src/ui/azure_maps_plugin_dialog_base.ui): Main UI file that shows the first dialog box customer interacts with.
- [azure_maps_plugin_floor_picker.ui](../../src/ui/azure_maps_plugin_floor_picker.ui): Floor picker file, shown once the plugin is loaded.
- [azure_maps_plugin_welcome_message.ui](../../src/ui/azure_maps_plugin_welcome_message.ui) Welcome Message

### QTDesigner
No need to do any setups, as everything has already been setup for us. <br/>
- Open the desired UI files in QTDesigner
- The right side shows two panes, Object inspector and Property Editor
    - Object Inspector: This shows the layout of the dialog box, i.e. what elements the dialog box is made of.
    - Property Editor: This shows the editable properties for the element currently selected in object inspector. 
- Add widgets by searching through the list on the left. 