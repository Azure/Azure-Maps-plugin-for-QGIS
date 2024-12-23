# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AzureMapsPlugin
                                 A QGIS plugin
 Azure Maps Creator plugin for QGIS
                              -------------------
        begin                : 2019-06-04
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Microsoft Corporation
        email                : tejitpabari@microsoft.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import time
import inspect
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *

# Initialize Qt resources from file resources.py
from .helpers.Constants import Constants
from .resources import *

# Import the code for the dialog
from .azure_maps_plugin_dialog import AzureMapsPluginDialog

from .helpers.progress_iterator import ProgressIterator
from .helpers.level_picker import LevelPicker
from .helpers.validation_utility import ValidationUtility
from .helpers.AzureMapsPluginLogger import AzureMapsPluginLogger
from .helpers.AzureMapsPluginDialogBox import AzureMapsPluginDialogBox
from .helpers.AzureMapsPluginRequestHandler import AzureMapsPluginRequestHandler
from .helpers.AzureMapsPluginMessageBar import AzureMapsPluginMessageBar

from shapely.geometry import mapping, shape

import os.path
import urllib.parse
import json

class AzureMapsPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.dlg = AzureMapsPluginDialog(self.iface)
        self.ltv = self.iface.layerTreeView()
        self.pluginToolBar = self.iface.pluginToolBar()
        self.model = self.ltv.layerTreeModel()
        self.root = QgsProject.instance().layerTreeRoot()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        QgsApplication.setAttribute(Qt.AA_Use96Dpi)
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "AzureMapsPlugin_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.current_dataset_id = None
        self.ontology = None
        self.current_index = None
        self.collectionName_collectionDef_map = {}
        self.relation_map = {}
        self.enum_ids = {}
        self.areFieldsValid = {}
        self.saveFailedClasses = set()
        self.base_group = None
        self.apiName = Constants.FEATURES
        self.apiVersion = Constants.API_Versions.V20230301PREVIEW
        self.internalDelete = False

        self.dialogBox = AzureMapsPluginDialogBox(self.iface)
        self._create_helpers()

    def _create_helpers(self):
        """Create helpers for the plugin. Setup Logger and AzureMapsRequestHandler"""
        self.logger = AzureMapsPluginLogger(self.iface,
                            hideSubscriptionKey=True,
                            subscription_key=self.dlg.subKey.text(),
                            autoLogToFile=True,
                            logFolder=self.dlg.logsFolderPicker.filePath(), 
                            debugLog=False)
        self.requestHandler = AzureMapsPluginRequestHandler(
            subscription_key=self._get_subscription_key(),
            geography=self.dlg.geographyDropdown.currentText(),
            api_version=self.apiVersion,
            logger=self.logger
        )
        self.msgBar = AzureMapsPluginMessageBar(self.iface, logger=self.logger)
    
    def _setup_helpers(self):
        """Setup helpers once the parameters are set by the user."""
        self.logger.set_parameters(
            subscription_key=self._get_subscription_key(),
            dataset_id=self._get_datasetId(),
            logFolder=self._get_logs_folder()
        )
        self.requestHandler.set_parameters(
            subscription_key=self._get_subscription_key(),
            geography=self._get_geography(),
            api_version=self.apiVersion,
            logger=self.logger
        )
        self.msgBar.set_parameters(logger=self.logger)

    def _get_subscription_key(self):
        return self.dlg.subKey.text()
    
    def _get_datasetId(self):
        return self.dlg.datasetId.currentText()
    
    def _get_geography(self):
        return self.dlg.geographyDropdown.currentText()
    
    def _get_logs_folder(self):
        return self.dlg.logsFolderPicker.filePath()

    def translate(self):
        """Get the translation for plugin name using Qt translation API."""
        return QCoreApplication.translate("AzureMapsPlugin", Constants.AzureMapsQGISPlugin.AUTHOR)

    def add_action(self):
        """Add a toolbar icon to the toolbar."""
        icon = QIcon(Constants.Paths.PLUGIN_CIRCLE_ICON)
        
        # Make the action
        text = self.translate()
        parent = self.iface.mainWindow()
        callback = self.run
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)

        # Setup other configs
        action.setEnabled(True)
        action.setCheckable(True)
        action.setChecked(False)

        # Add tooltips
        tooltip_text = "Azure Maps Creator Plugin"
        action.setStatusTip(tooltip_text)
        action.setWhatsThis(tooltip_text)
        self.iface.addToolBarIcon(action) # Adds plugin icon to Plugins toolbar
        # self.iface.addPluginToVectorMenu(self.menu, action) # Adds plugin icon to Vector menu
        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Add the plugin icon on the Plugin Toolbar
        config_path = (
            QgsApplication.qgisSettingsDirPath().replace("\\", "/")
            + Constants.Paths.RELATIVE_CONFIG_PATH
        )
        plugin_settings = QSettings(config_path, QSettings.IniFormat)
        self.add_action()

        # If plugin has been installed for the first time, show a welcome message
        if plugin_settings.value("freshinstall", "true").lower() == 'true':
            plugin_settings.setValue("freshinstall", "false")
            self._open_welcome_message()

        self._open_deprecation_message()

        # Initialize Level Control
        self._configure_level_picker()

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.translate(), action)
            self.iface.removeToolBarIcon(action)

        # Delete toolbar level picker on plugin unload
        if hasattr(self, "toolbar_level_combobox_action"):
            self.pluginToolBar.removeAction(self.toolbar_level_combobox_action)

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg.getFeaturesButton.clicked.connect(self.get_features_clicked)
            self.dlg.listDatasetButton.clicked.connect(self.list_datasets_clicked)
            self.dlg.datasetId.currentTextChanged.connect(lambda text: self.list_datasets_changed(text))
            self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

        # Close dialog if it is already open - mocks dialog toggle behavior
        if self.dlg.isVisible():
            self.dlg.hide()
            return

        self._getFeaturesButton_setEnabled(True)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

    def close_button_clicked(self):
        self.dlg.hide()
        self.actions[0].setChecked(False)

    def _layer_setSubsetString_floorpicker(self, layer, ordinal):
        if isinstance(layer, QgsVectorLayer) and (layer.name() in self.layerName_collectionName_map):
            if self._is_field_exist_layer(layer, "floor"):
                layer.rollBack()
                layer.setSubsetString("floor = {} OR floor is NULL".format(ordinal))

    def refresh_floor_picker(self):
        self.floor_picker_changed(self.level_picker.get_index())

    def _get_QActions(self, *args):
        for actionName in args:
            yield self.iface.mainWindow().findChild(QAction, actionName)
            
    def _reset_feature_selection(self):
        for action in self._get_QActions('mActionDeselectAll', 'mClearResultsAction'):
            if action: action.trigger()

    def floor_picker_changed(self, index):
        """
        Change the floor picker to the given index
        :param index: The index of the floor to change to. Indexing should start from 0
        """
        if index < 0: return # Index cannot be lower than 0
        if self.current_index == index: return # No action if index is the same as current index

        self._reset_feature_selection()
        ordinal = str(self.level_picker.get_ordinal(index)) # Get ordinal on index
        self.current_index = index 
        for toplevel_layer in QgsProject.instance().layerTreeRoot().children():
            for child_treeLayer in toplevel_layer.children():
                if isinstance(child_treeLayer, QgsLayerTreeLayer):
                    self._layer_setSubsetString_floorpicker(child_treeLayer.layer(), ordinal)
                elif isinstance(child_treeLayer, QgsLayerTreeGroup):
                    for child in child_treeLayer.children():
                        if isinstance(child, QgsLayerTreeLayer):
                            self._layer_setSubsetString_floorpicker(child.layer(), ordinal)

        for group in self.root.children():
            for child in group.children():
                if isinstance(child, QgsLayerTreeLayer):
                    self._layer_setSubsetString_floorpicker(child.layer(), ordinal)

    def set_creator_status(self, status):
        self.dlg.creatorStatus.setText(status)
        self.dlg.creatorStatus_2.setText(status)
        QApplication.processEvents()
    
    def _get_request_base_error(self, resp, base_error, progress):
        """
        Error handling for get requests
        Show error message on message bar
        Stop progress bar
        """
        if resp["error_text"]:
            error_text = "{} Please try again. Error: {}".format(base_error, resp["error_text"])
            if "response" in resp and resp["response"]: # status code is available
                error_text = "{} Response status code {}. Error: {}".format(
                        base_error, resp["response"].status_code, resp["error_text"])
            self.dialogBox.QMessageCrit(
                title="Dataset error",
                text=base_error,
                detailedText=error_text
            )
            self.logger.QLogCrit(error_text + "Response: {}".format(resp["response"]))
            self.reset(progress)
            return False
        return True
    
    def reset(self, progress=None):
        # Clear QGIS layers
        if self.base_group in self.root.children():
            self.root.removeChildNode(self.base_group)
        # Clear internal variables
        self.base_group = None # Remove base group
        self.current_dataset_id = None # Remove current dataset ID
        self.level_picker = LevelPicker([self.toolbar_level_picker])
        self.current_index = None
        self.id_map = {} # Clear id map
        if progress: # Close progress bar
            progress.close()
    
    def _get_layer_config(self, layer):
        """Returns a dictionary with the layer configuration, useful for creating widgets"""
        return {
            "Layer": layer,
            "LayerName": layer.name(),
            "Key": "id",
            "Value": "name",
            "OrderByValue": True,
        }
    
    def _add_attribute(self, layer, attribute_name, attribute_type=QVariant.String, hidden=False):
        """Adds an attribute to a layer if it doesn't exist already"""
        index = layer.dataProvider().fieldNameIndex(attribute_name)
        if index == -1: # attribute doesn't exist
            provider = layer.dataProvider()
            layer.startEditing()
            field = QgsField(attribute_name, attribute_type)
            provider.addAttributes([field])
            layer.updateFields()
            if hidden: # optionally hide attribute
                self._hide_attribute(layer, attribute_index=provider.fieldNameIndex(attribute_name))
            return provider.fieldNameIndex(attribute_name)
        return index

    def _add_widget(self, layer, attribute_name, attribute_type=QVariant.String, widget_type="ValueRelation", config={}):
        """Adds a widget to an attribute if it doesn't exist already"""
        index = self._get_layer_field_index(layer, attribute_name)
        if index == -1: # attribute doesn't exist
            attribute_index = self._add_attribute(layer, attribute_name, attribute_type) # add attribute
            self._add_widget_attribute(layer, widget_type, attribute_name=None, attribute_index=attribute_index, config=config) # add widget to attribute
            return attribute_index
        return index
    
    def _add_widget_attribute(self, layer, widget_type, attribute_name=None, attribute_index=-1, config={}):
        if attribute_name:
            attribute_index = self._get_layer_field_index(layer, attribute_name)
        if attribute_index != -1:
            widget = QgsEditorWidgetSetup(widget_type, config) # create widget with attribute
            layer.setEditorWidgetSetup(attribute_index, widget)

    def _hide_attribute(self, layer, attribute_name=None, attribute_index=-1, config={}):
        """Hides an attribute from a layer"""
        self._add_widget_attribute(layer, "Hidden", attribute_name, attribute_index, config)
    
    def _get_feature_attribute(self, feature, attribute_name, default_value=None):
        """Gets an attribute from a feature if it has a value, else returns None"""
        try:
            value = feature[attribute_name]
            if value == None:
                return default_value
            return value
        except KeyError: # QGIS returns key error, if attribute doesn't exist
            return default_value
        
    def _get_feature_attributes(self, feature, attribute_names, default_value=None):
        """Gets multiple attributes from a feature if they have a value, else returns None"""
        attributes = []
        for attribute_name in attribute_names:
            attributes.append(self._get_feature_attribute(feature, attribute_name, default_value))
        return attributes
        
    def _is_field_exist(self, feature, field_name):
        """Checks if a field exists in a feature"""
        fieldIndex = self._get_feature_field_index(feature, field_name)
        return fieldIndex != -1
    
    def _is_field_exist_layer(self, layer, field_name):
        """Checks if a field exists in a layer"""
        fieldIndex = self._get_layer_field_index(layer, field_name)
        return fieldIndex != -1
    
    def _get_feature_field_index(self, feature, field_name):
        return feature.fieldNameIndex(field_name)
    
    def _get_layer_field_index(self, layer, field_name):
        return layer.fields().indexFromName(field_name)
    
    def _get_feature_field_index_value(self, feature, field_name, default_value=None):
        fieldIndex = self._get_feature_field_index(feature, field_name)
        if fieldIndex != -1:
            return fieldIndex, self._get_feature_attribute(feature, field_name, default_value)
        return fieldIndex, default_value
        
    def _get_attribute_table_config(self, layer, ontologyClass, additional_hidden_attributes=[]):
        """Returns a QgsAttributeTableConfig object with the desired settings"""
        table_config = layer.attributeTableConfig()
        table_config.setActionWidgetStyle(QgsAttributeTableConfig.ActionWidgetStyle.DropDown)
        for hidden_attribute in ontologyClass.BASE_ATTR.hiddenProperties + additional_hidden_attributes:
            attribute_index = self._get_layer_field_index(layer, hidden_attribute)
            if attribute_index != -1:
                table_config.setColumnHidden(attribute_index, True)
        return table_config
    
    def _get_editor_form_config(self, layer, ontologyClass, readOnlyAttributes=[]):
        form_config = layer.editFormConfig()
        for attribute_name in readOnlyAttributes:
            attribute_index = self._get_layer_field_index(layer, attribute_name)
            if attribute_index != -1:
                form_config.setReadOnly(attribute_index, True)
        return form_config

    def _set_layer_labeling(self, layer, geometryType):
        """Sets the labeling for a layer, based on geometryType"""
        layer_settings  = QgsPalLayerSettings()
        renderer = layer.renderer()
        symbol = None if not renderer else renderer.symbol()
        if geometryType == Constants.GEOMETRY_TYPE.POLYGON or geometryType == Constants.GEOMETRY_TYPE.MULTIPOLYGON:
            layer_settings.fieldName = "name" # field of feature to use for labeling
            layer_settings.FontSizeUnit = 9 # font size
            layer_settings.enabled = True
            layer_settings.Color = QColor.fromRgb(255,0,0) # Label color
            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
            layer.setLabelsEnabled(True) # enable labeling
            layer.setLabeling(layer_settings)

            if symbol: symbol.setColor(QColor.fromRgb(0,0,0,0))
        else:
            if symbol: symbol.setColor(QColor.fromRgb(0,0,0))
        
        layer.triggerRepaint() 
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

    def list_datasets_clicked(self):
        self._setup_helpers() # setup helper classes
        progress = ProgressIterator(
            msg="Fetching Dataset Information...", window_title="Fetching Datasets",
            setCancelButtonNone=True, disableCloseButton=True, alwaysOnTop=False
        )
        progress.show()
        QApplication.processEvents()
        progress.set_maximum(2)

        self.datasets_url = Constants.API_Paths.LIST_DATASETS.format(host=self.requestHandler.host)
        resp = self.requestHandler.get_request(self.datasets_url)
        success = self._get_request_base_error(resp, resp["error_text"], progress) # call error handling function
        if not success: return
        progress.next("Parsing Dataset Information...")
        r = resp["response"]
        dataset_ids_descriptions = [(dataset.get("datasetId", None), 
                                     dataset.get("description", "--No Description--"), 
                                     dataset.get('created', ''))
                                     for dataset in r.get("datasets",[])]
        dataset_ids_descriptions.sort(key=lambda x: x[2], reverse=True)
        self.dlg.datasetId.clear()
        self.dlg.datasetId.addItems(['{}\n{}'.format(uid, d) for uid, d, _ in dataset_ids_descriptions if uid != None])

    def list_datasets_changed(self, text):
        self.dlg.datasetId.setEditText(text.split('\n')[0].strip())

    def get_features_clicked(self):
        # Condition: Only one dataset is allowed at a time
        dataset_id = self._get_datasetId()
        if self.current_dataset_id is not None and len(self.root.children())>0:
            warning_response = self.dialogBox.QMessageWarn(
                title="Warning",
                text="""We can only load one dataset at a time. 
                        \nWould you like to remove the existing dataset and load a new dataset?\n\n
                        To remove: {} \nTo add: {}""".format(self.current_dataset_id, dataset_id),
                buttons=QMessageBox.Yes | QMessageBox.Cancel,
            )

            if warning_response == QMessageBox.Cancel:
                return self._getFeaturesButton_setEnabled(True)
            if warning_response == QMessageBox.Yes:
                pass # Keep going
            else:
                self.msgBar.QMessageBarCrit(
                    title="Error",
                    text="An unexpected error has occurred.",
                )
                return self._getFeaturesButton_setEnabled(True)

        self.close_button_clicked()
        self._getFeaturesButton_setEnabled(False)
        self._setup_helpers()

        start_time = time.time()

        # Start progress dialog
        progress = ProgressIterator(
            msg="Loading Dataset...", window_title="Retrieving features",
            setCancelButtonNone=True, disableCloseButton=True, alwaysOnTop=False
        )
        progress.show()  # Immediately show the progress bar
        QApplication.processEvents()

        # Get dataset metadata.
        self.features_url = Constants.API_Paths.BASE.format(host=self.requestHandler.host, apiName=self.apiName, datasetId=dataset_id)
        resp = self.requestHandler.get_request(Constants.API_Paths.GET_COLLECTIONS.format(base=self.features_url))
        success = self._get_request_base_error(resp, resp["error_text"], progress) # call error handling function
        if not success:
            return self._getFeaturesButton_setEnabled(True)
        
        r = resp["response"]
        self.ontology = r["ontology"]

                
        # After first call has been made, i.e. we can connect and datasetId is valid, remove existing dataset
        self.reset()
        self.logger.QLogInfo("{} Loading Azure Maps Creator dataset with ID: {} {}".format('-'*15, dataset_id, '-'*15))
        self.current_dataset_id = dataset_id
        # Create a new dataset group layer if it doesn't exist, otherwise override the existing group layer
        if self.base_group is None:
            self.base_group = self.root.insertGroup(0, dataset_id)
        else:
            self.base_group.removeAllChildren()
            self.base_group.setName(dataset_id)
        # Add a group layer delete event listener
        self.root.removedChildren.connect(self._on_layer_removed)

        # Get features from each collection.
        collections = r["collections"]

        # Set progress bar max value
        # We loop through definition and data for each collection, hence the 2*len(collections).
        # +3 is for other three progress.next statements we have scattered throughout the code
        #   - 1:"Loading Dataset..."; 2:"Adding Creator attributes..."; 3: "Dataset loaded successfully."
        numberOfCollections = len(collections) # Number of collections
        progress_max = 2*(numberOfCollections) + 3
        progress.set_maximum(progress_max)

        # Loop through collections and create tasks to get data and metadata(definition)
        taskList = []
        for collection in collections:
            collectionName = collection["id"]
            links = collection["links"]

            data_link = next(link for link in links if link["rel"] == "items")
            globals()['data_task_'+collectionName] = QgsTask.fromFunction(
                "Getting " + collectionName + " collection",
                self.requestHandler.get_request_parallel,
                collectionName, "data", data_link["href"]
            )
            QgsApplication.taskManager().addTask(globals()['data_task_'+collectionName]) # Add task to global queue
            taskList.append(globals()['data_task_'+collectionName]) # Add task to local list

            meta_link = next(link for link in links if link["rel"] == "describedBy")
            globals()['definition_task_'+collectionName] = QgsTask.fromFunction(
                "Getting " + collectionName + " collection definition",
                self.requestHandler.get_request_parallel,
                collectionName, "definition", meta_link["href"]
            )
            QgsApplication.taskManager().addTask(globals()['definition_task_'+collectionName])
            taskList.append(globals()['definition_task_'+collectionName])
        
        if not taskList:
            # If no tasks were created, request failed (since it failed to fetch the data or definition)
            return self._get_request_base_error({"error_text": "Error in fetching data from server"}, 
                                         "Unable to read collections data", progress)

        """
        Loop through all tasks and wait for them to finish
        collectionName_data_response_map = map of collectionName and data responses.
        collectionName_meta_response_map = map of collectionName and definition responses.
        Response maps are used to store the responses of the tasks
        All tasks have finished when the length of response maps = number of collections

        Need to use this manual method, instead of QgsTaskManager.countActiveTasks(), since the latter does not work properly with plugins
        neither does QgsTask.isActive() or QgsTask.isCanceled() work properly
        """
        progress.next("Loading Dataset...")
        collectionName_data_response_map, collectionName_meta_response_map = {}, {}
        while (len(collectionName_data_response_map) != numberOfCollections) or (len(collectionName_meta_response_map) != numberOfCollections): 
            for task in taskList:
                collectionName, request_type = task.args[0], task.args[1] # Get the collectionName and requestType from the task
                if request_type == "data": # If the task is a data task
                    if collectionName in collectionName_data_response_map: # If we have already stored the response in response map
                        continue
                    elif task.returned_values is not None: # If the task finished, store the response in response map
                        collectionName_data_response_map[collectionName] = task.returned_values
                        progress.next("Loading Dataset...")
                        self.msgBar.pop() # Removes the task complete message that comes from QGSTaskManager
                    elif task.exception is not None: # If the task failed, store the error in response map
                        error_json = {"error_text":task.exception, "success":False, "response":None}
                        collectionName_data_response_map[collectionName] = error_json
                        break
                elif request_type == "definition": # If the task is a definition task
                    if collectionName in collectionName_meta_response_map: # If we have already stored the response in response map
                        continue
                    elif task.returned_values is not None: # If the task finished, store the response in response map
                        collectionName_meta_response_map[collectionName] = task.returned_values
                        progress.next("Loading Dataset...")
                        self.msgBar.pop() # Removes the task complete message that comes from QGSTaskManager
                    elif task.exception is not None: # If the task failed, store the error in response map
                        error_json = {"error_text":task.exception, "success":False, "response":None}
                        collectionName_meta_response_map[collectionName] = error_json
                        break

        QgsApplication.taskManager().cancelAll() # Cancel all tasks

        _layerName_collectionName_map, _collectionName_layerName_list_map = {}, {} # Map of layerName to collectionName, Map of collectionName to layer list
        _layerName_layer_map, _layerName_config_map = {}, {} # Map of layerName and layer, Map of layerName and config
        _collectionName_referential_integrity_map = {} # Map of collectionName and referential integrity
        _collectionName_required_properties_list_map = {} # Map of collectionName and required properties list
        _layerName_geometryType_map = {} # Map of layerName and geometryType
        _collectionName_geometryCollection_map = {} # Map of collectionName and geometryCollection
        for collectionName in Constants.Ontology.get_display_order(self.ontology, collections):
            try:
                # Handle metadata response
                meta_response = collectionName_meta_response_map[collectionName]
                success = self._get_request_base_error(meta_response, "Unable to read {} collection definition".format(collectionName), progress) # Handle error
                if not success: return
                self.logger.QLogDebug("Loading {} collection definition".format(collectionName))
                self.collectionName_collectionDef_map[collectionName] = meta_response["response"] # Store the definition in schema map
                
                # Handle data response
                data_response = collectionName_data_response_map[collectionName]
                success = self._get_request_base_error(data_response, "Unable to read {} collection".format(collectionName), progress) # Handle error
                if not success: return
                self.logger.QLogDebug("Loading {} collection".format(collectionName))
                # Load the data of the collection into a layer
                geometryType_layer_map, referential_integrity_map, required_properties_list, geometryCollectionList = \
                    self.load_items(collectionName, data_response, 
                                    self.collectionName_collectionDef_map[collectionName], self.base_group)

                # Update the mapping
                _layerName_collectionName_map.update({l.name(): collectionName for l in geometryType_layer_map.values()}) # Update the layerName to collectionName map
                _collectionName_layerName_list_map[collectionName] = [l.name() for l in geometryType_layer_map.values()] # Update the collectionName to layer list map
                _layerName_layer_map.update({l.name(): l for l in geometryType_layer_map.values()}) # Update the layerName to layer map
                _layerName_config_map.update({l.name(): self._get_layer_config(l) for l in geometryType_layer_map.values()}) # Update the layerName to config map
                _collectionName_referential_integrity_map[collectionName] = referential_integrity_map  # Update the collectionName to referential integrity map
                _collectionName_required_properties_list_map[collectionName] = required_properties_list # Update the collectionName to required properties list
                _layerName_geometryType_map.update({l.name(): geometryType for geometryType, l in geometryType_layer_map.items()}) # Update the layerName to geometryType map
                _collectionName_geometryCollection_map[collectionName] = [f["id"] for f in geometryCollectionList] # Update the collectionName to geometryCollection map
            except Exception as e: # Handles any accidental errors that may occur, especially in the load_items function
                return self._get_request_base_error({"error_text": str(e)}, "Unable to load {} layer".format(collectionName), progress)
        
        self.layerName_collectionName_map, self.collectionName_layerName_list_map = _layerName_collectionName_map, _collectionName_layerName_list_map
        self.layerName_layer_map, self.layerName_geometryType = _layerName_layer_map, _layerName_geometryType_map
        self.collectionName_referential_integrity_map, self.collectionName_required_properties_list_map = _collectionName_referential_integrity_map, _collectionName_required_properties_list_map
        
        self.logger.QLogInfo("Loading collections successful!")
        self.logger.QLogInfo('\t'.join(['{}: {}'.format(collectionName, 
                                                        sum([_layerName_layer_map[lName].featureCount() 
                                                             for lName in _collectionName_layerName_list_map[collectionName]])) 
                                        for collectionName in Constants.Ontology.get_display_order(self.ontology, collections)]))
        
        progress.next("Adding Creator attributes...")
        self.logger.QLogInfo("Adding Creator attributes")

        """
        QGIS doesn't support geometryCollection and hence the features won't be rendered.
        Send a warning if geometryCollection is found. Add layer name and feature id to logs.
        """
        geometryCollectionFound, geometryCollectionStringList = False, []
        for cName, geometryCollectionList in _collectionName_geometryCollection_map.items():
            if len(geometryCollectionList) > 0:
                geometryCollectionFound = True
                geometryCollectionStringList.append("Layer {} with feature Ids: [{}]".format(cName, ', '.join(geometryCollectionList)))
        if geometryCollectionFound:
            self.msgBar.QMessageBarWarn(
                title = "Geometry Collection found in layers",
                text = """Layers with geometry type geometryCollection found. 
QGIS doesn't support this type and hence these features won't be rendered. Please check logs for more information"""
            )
            self.logger.QLogWarn("""Geometry Collection found in layers. 
QGIS doesn't support this type and hence these features won't be rendered. The features are affected: {}""".format(', '.join(geometryCollectionStringList)))
            
        _levelId_ordinal_map, _ordinal_levelId_map = {}, {}
        _unitId_ordinal_map = {}
        loading_order = []
        for cName in Constants.Ontology.get_loading_order(self.ontology, collections):
            loading_order.extend(sorted(_collectionName_layerName_list_map[cName]))

        for order_ind, layerName in enumerate(loading_order):
            additional_hidden_attributes = [] # Attributes that are hidden, such as referential Integrity attributes etc.
            readOnly_attributes = ["id"] # All layers have id attribute which is read only
            collectionName = _layerName_collectionName_map[layerName]
            layer = _layerName_layer_map[layerName]
            geometryType = _layerName_geometryType_map[layerName]
            self.logger.QLogDebug("Adding {} featureClass attributes".format(layerName))
            
            self._set_layer_labeling(layer, geometryType)
            QApplication.processEvents()
                
            if self.ontology == Constants.Ontology.FACILITY_2:
                ontologyClass = Constants.Facility_2 
            elif self.ontology == Constants.Ontology.CUSTOM:
                ontologyClass = Constants.CustomOntology
            else:
                raise Exception("Ontology not supported")

            referential_integrity_map = _collectionName_referential_integrity_map[collectionName]
            # Handling levelId integretiy for custom ontology 
            if self.ontology == Constants.Ontology.CUSTOM and \
                Constants.CustomOntology.COLLECTIONS.LVL in self.collectionName_layerName_list_map and \
                    self._get_layer_field_index(layer, "levelId") != -1: # levels exist
                referential_integrity_map["level"] = "levelId"

            required_properties_list = _collectionName_required_properties_list_map[collectionName]
            geometryType = _layerName_geometryType_map[layerName]
            
            # Add a widget for each referential integrety field
            # And add those fields to the hidden attributes list
            ref_field_id_widget_index_map = {}
            for ref_field_name, ref_field_id in referential_integrity_map.items():
                widget_index = -1
                for layerName in _collectionName_layerName_list_map[ref_field_name]:
                    widget_index = self._add_widget(layer=layer, attribute_name=ref_field_name, attribute_type=QVariant.String,
                                                widget_type="ValueRelation", config=_layerName_config_map[layerName])
                ref_field_id_widget_index_map[ref_field_id] = widget_index
                additional_hidden_attributes.append(ref_field_id)
                
            floor_index = None
            # Loop through all features and apply necessary changes (add floor attribute, add referential integrity widgets)
            for feature in layer.getFeatures():
                featureId = self._get_feature_attribute(feature, "id")
                ordinal = self._get_feature_attribute(feature, "ordinal")
                levelId, unitId = self._get_feature_attribute(feature, "levelId"), self._get_feature_attribute(feature, "unitId")
                is_floor = True

                # If level layer, ordinal is not NULL, add ordinal to layerId--ordinal map
                # Otherwise, ordinal is NULL, get ordinal from levelId (or unitId in case of facility ontology)
                if collectionName.lower() == "facility": continue
                elif collectionName.lower() == "level":
                    _levelId_ordinal_map[featureId] = ordinal
                    _ordinal_levelId_map[ordinal] = featureId
                else: 
                    if levelId != None and levelId in _levelId_ordinal_map:
                        ordinal = _levelId_ordinal_map[levelId]
                    elif unitId != None and unitId in _unitId_ordinal_map and self.ontology == Constants.Ontology.FACILITY_2: # In case of areaElement, lineElement, pointElement
                        ordinal = _unitId_ordinal_map[unitId]
                    elif len(_levelId_ordinal_map) > 0:
                        # If levelId or unitId is not present, but levels are still present
                        # I.e. Features without levelId, added to all levels
                        is_floor = False
                        self.logger.QLogInfo("Feature with id:{} is not attached to a floor".format(featureId))
                    else: # Else would be noontology scenario, where no levels are present - do nothing
                        is_floor = False
                        
                # Handling Facility2.0 ontology scenario, add ordinal to unitId--ordinal map
                if collectionName == "unit" and self.ontology == Constants.Ontology.FACILITY_2: 
                    _unitId_ordinal_map[featureId] = ordinal
                if collectionName == "facility":
                    self._update_layer_group_name(layer)

                # If floor attribute exists, create floor attribute if it doesn't exists and add ordinal to floor attribute
                if is_floor:
                    if floor_index == None: # Only happens once per layer
                        """
                        Add floor attribute - seperate attribute needed since only level featureClass has ordinals (floor numbers)
                        Most have levelId (and unitId, in case of Facility2.0 Ontology), which can be used to extract ordinals
                        This helps to store ordinals in all featureClasses
                        """
                        # If the layer has no geometry, or if it is a facility layer - we don't need to add floors
                        if geometryType == Constants.GEOMETRY_TYPE.NOGEOMETRY or collectionName == "facility": 
                            floor_index = -1
                        else:
                            floor_index = self._add_attribute(layer=layer, attribute_name="floor", attribute_type=QVariant.String, hidden=False)
                            # layer.setDefaultValueDefinition(floor_index, QgsDefaultValue("'--Current Floor--'"))

                    if floor_index != -1:
                        layer.changeAttributeValue(feature.id(), floor_index, ordinal)

                # Add referential integrity values to referential integrity fields
                # For Facility2.0, category and directory Info layers would not have any referential integrity fields
                for ref_field_id, widget_index in ref_field_id_widget_index_map.items():
                    layer.changeAttributeValue(feature.id(), widget_index, self._get_feature_attribute(feature, ref_field_id))
            
            if floor_index != -1: # If floor attribute exists, it is readOnly and levelId is hidden
                if self._get_layer_field_index(layer, "floor") != -1:
                    additional_hidden_attributes.append("floor")
                if self._get_layer_field_index(layer, "level") != -1:
                    readOnly_attributes.append("level")
                if self._get_layer_field_index(layer, "levelId") != -1 and "levelId" not in additional_hidden_attributes:
                    additional_hidden_attributes.append("levelId")

            """Hide Attributes"""
            # In case of Custom Ontology, if level collectionName is present (i.e. levels are to be rendered)
            # Hide ordinal fields, since we have the floor field
            if self.ontology == Constants.Ontology.CUSTOM and Constants.CustomOntology.COLLECTIONS.LVL in self.collectionName_layerName_list_map:
                if self._get_layer_field_index(layer, "ordinal") != -1:
                    additional_hidden_attributes.append("ordinal")

            # Set attribute table config for layer and hide the hidden attributes + additional hidden attributes
            attribute_table_config = self._get_attribute_table_config(layer, ontologyClass, additional_hidden_attributes)
            layer.setAttributeTableConfig(attribute_table_config)
            for hidden_attribute in ontologyClass.BASE_ATTR.hiddenProperties + additional_hidden_attributes:
                self._hide_attribute(layer, attribute_name=hidden_attribute)
            
            """Set ReadOnly Attributes"""
            editor_form_config = self._get_editor_form_config(layer, ontologyClass, readOnly_attributes)
            layer.setEditFormConfig(editor_form_config)

            """Set NonNull Constraints"""
            # Set NonNull constraints for required properties
            for required_property in required_properties_list:
                field_index = self._get_layer_field_index(layer, required_property)
                layer.setFieldConstraint(field_index, QgsFieldConstraints.ConstraintNotNull)

            layer.commitChanges()
            self.add_layer_events(layer)
        
        if self.ontology == Constants.Ontology.CUSTOM:
            for collectionName in Constants.CustomOntology.COLLECTIONS.nonEditableCollections:
                for layerName in self.collectionName_layerName_list_map.get(collectionName, []):
                    layer = self.layerName_layer_map[layerName]
                    layer.setReadOnly(True)

        self.levelId_ordinal_map, self.ordinal_levelId_map = _levelId_ordinal_map, _ordinal_levelId_map
        self.unitId_ordinal_map = _unitId_ordinal_map
        if len(self.levelId_ordinal_map) != 0:
            self.level_picker.extend(sorted(self.levelId_ordinal_map.values()))
            self.level_picker.set_base_ordinal(0)

        # Set canvas CRS to WGS84 Pseudo-Mercator
        canvas_crs = QgsCoordinateReferenceSystem(Constants.CRS_EPSG_3857)
        self.iface.mapCanvas().setDestinationCrs(canvas_crs)

        self._getFeaturesButton_setEnabled(True)

        # zoom into unit layer after loading complete
        self.iface.zoomToActiveLayer()

        # Clean up to filter features by level and reset initial level to 0 if possible
        self.refresh_floor_picker()

        progress.next("Dataset loaded successfully.")
        self.logger.QLogInfo("{} Datset loaded successfully in {} seconds{}".format('-'*10, time.time()-start_time, '-'*10))
        # Close progress dialog
        progress.close()

    def add_layer_events(self, layer):
        """Add events/signals to layer"""
        layer.beforeCommitChanges.connect(lambda: self.on_before_commit_changes(layer))
        layer.featuresDeleted.connect(lambda fids: self.on_features_deleted(fids, layer))
        layer.featureAdded.connect(lambda fid: self.on_feature_added_or_changed(fid, layer))
        # layer.attributeValueChanged.connect( lambda fid: self.on_feature_added_or_changed(fid, layer) )
        layer.updatedFields.connect(lambda: self.on_fields_changed(layer))
        layer.afterCommitChanges.connect(lambda: self.on_after_commit_changes(layer))
        layer.beforeRollBack.connect(lambda: self.on_before_rollBack(layer))

    def on_before_rollBack(self, layer):
        self._handle_error_msgBar(layer.name(), False)

    def _handle_error_msgBar(self, layer_name, is_fail):
        """Handle the error display in message bar"""
        if is_fail: # If there is a failure, add to list of failed classes
            self.saveFailedClasses.add(layer_name)
        else: # If there is no failure, remove from list of failed classes
            self.saveFailedClasses.discard(layer_name)
        if self.saveFailedClasses: # If there are any failed classes, display the message bar
            saveFailedStrings = ['"{}"'.format(f) for f in self.saveFailedClasses]
            self.msgBar.QMessageBarPopPushCrit(
                title="Save Failed!",
                text="Your saves in {} layer(s) are still pending".format(', '.join(saveFailedStrings)),
                item_id="save_failed",
                showMore = """Your changes are still present in QGIS. Please fix the issues and try saving again.
Logs can be found at {}""".format(self.logger.errorLogFolderPath))
        else:
            self.msgBar.pop(item_id="save_failed")

    def _resolve_referential_integrity(self, field_info):
        """
        Resolve referential integrity for a field.
        If the field references another feature, return the featureId of that feature and field name.
        Eg:
        {"name": "categoryId", "required": true, "type": { "featureId": "category" }}
        Returns: "category", "categoryId"
        """
        field_name, field_type = field_info["name"], field_info["type"]
        if "featureId" in field_type:
            return field_type["featureId"], field_name
        return None, None
    
    def _split_response_by_geometry_type(self, response, geometryTypes):
        """
        Split response into a dictionary of geometry types.
        """
        geometryCollectionList = [] # Flag to check if GEOMETRYCOLLECTION geometry type is found
        response_by_geometry_type = {geometryType: None for geometryType in geometryTypes}
        if Constants.GEOMETRY_TYPE.INVALID in response_by_geometry_type: # Remove INVALID geometry type
            del response_by_geometry_type[Constants.GEOMETRY_TYPE.INVALID]
        if Constants.GEOMETRY_TYPE.GEOMETRYCOLLECTION in response_by_geometry_type: # Remove GEOMETRYCOLLECTION geometry type
            del response_by_geometry_type[Constants.GEOMETRY_TYPE.GEOMETRYCOLLECTION]
        for feature in response["features"]:
            if feature["geometry"] is None: # No geometry
                geometryType = Constants.GEOMETRY_TYPE.NOGEOMETRY
            else: # Geometry exists, get geometry type
                geometryType = Constants.GEOMETRY_TYPE(feature["geometry"]["type"])

            if geometryType == Constants.GEOMETRY_TYPE.INVALID: # Ignore INVALID geometry type
                continue 
            if geometryType == Constants.GEOMETRY_TYPE.GEOMETRYCOLLECTION: # GEOMETRYCOLLECTION geometry type found
                geometryCollectionList.append(feature)
                continue
            if geometryType not in response_by_geometry_type: # Throw exception if geometry type is not in defined list of geometry types.
                raise Exception("Geometry type {} not found in supported list of geometry types.".format(geometryType))
            
            # Add feature to dictionary of geometry types
            if response_by_geometry_type[geometryType] is None:
                response_by_geometry_type[geometryType] = {"type": "FeatureCollection", "features": []}
            response_by_geometry_type[geometryType]["features"].append(feature)
        return response_by_geometry_type, geometryCollectionList

    def load_items(self, name, response, collection_definition, group):
        """
        Main function to load all features from a feature class, in a response, to a layer.
        """
        response_json = response["response"]

        # Get properties from collection definition
        properties = collection_definition.get("properties", [])
        properties_map = {field["name"]: field for field in properties}

        # Get list of geometry types from collection definition. Throws exception if invalid geometry type.
        geometryTypeFromDefinition = collection_definition.get("geometryType", None)
        geometryTypes = Constants.GEOMETRY_TYPE.from_definition(geometryTypeFromDefinition) # Returns a list of geometry types.

        # Split response into a dictionary of geometry types.
        feature_collection_by_geometry_type, geometryCollectionList = self._split_response_by_geometry_type(response_json, geometryTypes)
        geometry_group = group
        # If there are multiple geometry types, create a group for the geometry types
        if len(feature_collection_by_geometry_type) > 1:
            geometry_group = group.addGroup(name)
            geometry_group.setExpanded(False)

        # For each geometry type, create a layer and add it to the group
        fullFieldString = None
        geometry_type_layer_map = {}
        referential_integrity_map, required_properties_list = {}, [] # Referential Integrerity Map, Required Properties Map
        for geometryType, feature_collection in feature_collection_by_geometry_type.items():
            # Make a temporary layer with the feature_collection
            temp_layer = QgsVectorLayer(json.dumps(feature_collection), "temp", "ogr")

            # Create a field string for the layer. Happens only once, for all geometry types since all geometry types have the same fields.
            if fullFieldString is None:
                """
                Load fields from temp_layer, to preserve ordering
                Copying features from temp_layer to layer happens via index (i.e. in order of occurance)
                If order of fields in temp_layer is not the same as the order of fields in the actual layer, data is copied incorrectly
                """
                field_order = [field.name() for field in temp_layer.fields()] # Get field order from temp_layer
                if len(field_order)> 0:
                    if "id" != field_order[0]:
                        self.logger.QLogDebug("Unable to load dataset. ID field not found in first position.", inspect_frame=inspect.currentframe())
                        raise Exception("Unable to load dataset.")
                    field_order.remove("id")
                # other fields from the collection definition. These can occur in any order, since no data was found for them in the temp_layer
                other_fields_order = [field["name"] for field in properties if field["name"] not in field_order]
                
                fieldString = []
                fieldString.append('field={}:{}'.format("id", Constants.FIELD_TYPE.STRING)) # ID is always first, and not defined in the properties
                for field_name in field_order + other_fields_order: # Combine field order and other fields
                    if field_name not in properties_map: continue
                    field = properties_map[field_name] # get info for the field from the collection definition
                    field_type = Constants.FIELD_TYPE.from_definition_type(field["type"])
                    
                    # Setup referential integrity map
                    ref_field_name, ref_field_id = self._resolve_referential_integrity(field)
                    if ref_field_name:
                        referential_integrity_map[ref_field_name] = ref_field_id
                    
                    # Setup required properties map
                    if field.get("required", False):
                        required_properties_list.append(field_name)
                    fieldString.append('field={}:{}'.format(field_name, field_type))
                fullFieldString = '&'.join(fieldString)
            
            # Layer name is the collection name, unless there are multiple geometry types, in which case the geometry type is appended to the name
            layer_name = "{}{}{}".format(name, Constants.LAYER_NAME_DELIMITER, geometryType) if len(feature_collection_by_geometry_type) > 1 else name

            # Define the actual layer, with the layer name and specified fields
            layer = QgsVectorLayer(
                Constants.QGIS_VECTOR_LAYER_URI.format(geometryType=geometryType, crs=Constants.CRS_EPSG_4326, fieldString=fullFieldString),
                layer_name,
                "memory"
                )

            # Add any leftover attributes from the temp layer to actual layer
            layer.dataProvider().addAttributes(temp_layer.dataProvider().fields().toList())
            layer.updateFields()
            
            # Add layer to project, ready for display
            QgsProject.instance().addMapLayer(layer, False)
            geometry_group.addLayer(layer)

            # Add any fields defined in actual layer, to the temp layer
            # This is needed because to copy over data from the temp layer to the actual layer, we need to have the same fields in both
            layer.startEditing()
            qlr_fields = [field for field in layer.fields()]
            api_fields_name_set = set([field.name() for field in temp_layer.fields()])
            for qlr_field in qlr_fields:
                if qlr_field.name() not in api_fields_name_set:
                    field_type = qlr_field.type()
                    if field_type == QVariant.String:
                        set_expression = ""
                    elif field_type == QVariant.Bool:
                        set_expression = "False"
                    else:
                        set_expression = None
                    temp_layer.addExpressionField(set_expression, qlr_field)
            
            # Add the data from the temp layer to the actual layer
            success = layer.addFeatures(temp_layer.getFeatures())

            # BUG: Delete the anchorPoint field, if it exists
            anchorIndex = layer.dataProvider().fieldNameIndex("anchorPoint")
            if anchorIndex != -1:
                result = layer.dataProvider().deleteAttributes([anchorIndex])
                layer.updateFields()

            layer.setDefaultValueDefinition(self._get_layer_field_index(layer, "id"), QgsDefaultValue("'--ID will be generated by server--'"))
            
            layer.commitChanges() # Commit pending changes to the actual layer

            # Store the id of each feature in a map, so we can use it later to update the feature
            for feature in layer.getFeatures():
                self.id_map[layer.name() + ":" + str(feature.id())] = self._get_feature_attribute(feature, "id")
            
            geometry_type_layer_map[geometryType] = layer
        return geometry_type_layer_map, referential_integrity_map, required_properties_list, geometryCollectionList

    def on_fields_changed(self, layer):
        self.dialogBox.QMessageWarn(
            title="Change fields",
            text="Fields are immutable on {} layer.".format(layer.name()),
            detailedText="""Please do not manually change fields on this layer. 
                            Otherwise, you may experience failures on saving your data.""",
        )

    def _is_string_field_valid(self, feature, field_name, check_func=None):
        if self._is_field_exist(feature, field_name):
            value = self._get_feature_attribute(feature, field_name, "")
            if value and value.strip() and value != "NULL" and check_func(value): 
                return True
        return False
    
    def _string_field_valid(self, feature, field_name, check_func=None):
        is_valid = self._is_string_field_valid(feature, field_name, check_func)
        if not is_valid:
            self.msgBar.QMessageBarWarn(
                title="Warning",
                text="{} is required.".format(field_name),
                duration=10
            )
        return is_valid

    def on_feature_added_or_changed(self, fid, layer):
        # BUG: Handle feature validation based on required fields
        self.areFieldsValid[fid] = True # Set the flag to true, make it false if any of the checks fail

    def on_features_deleted(self, feature_ids, layer):
        if self.internalDelete:
            self.internalDelete = False
            return

        for fid in feature_ids:
            if fid in self.areFieldsValid.keys():
                self.areFieldsValid.pop(fid)

        edits = layer.editBuffer()
        deletes = edits.deletedFeatureIds()
        for fid in deletes:
            key = layer.name() + ":" + str(fid)
            # raise confirmation dialog for deleting committed features
            if key in self.id_map:
                warning_response = self.dialogBox.QMessageWarn(
                    title = "Deleting Features in {} layer".format(layer.name()),
                    text = "Are you sure to delete these features?",
                    buttons = QMessageBox.Yes | QMessageBox.Cancel,
                    detailedText="""Please make sure other layers are not referencing these features before deleting them.
Otherwise, the delete operation will fail."""
                )
                if warning_response == QMessageBox.Cancel:
                    # Stop a current editing operation and discards any uncommitted edits
                    layer.rollBack()
                    return
                elif warning_response == QMessageBox.Yes:
                    return
    
    def on_after_commit_changes(self, layer):
        for feature in layer.getFeatures():
            if '{}:{}'.format(layer.name(), feature.id()) not in self.id_map:
                self.id_map['{}:{}'.format(layer.name(), feature.id())] = self._get_feature_attribute(feature, "id")

        for _, feature, _ in self.failAdd:
            layer.addFeature(feature)
                
        # Looping through edits
        for _, (feature, oldFeature), _ in self.failEdit:
            fid, featureId = feature.id(), self._get_feature_attribute(feature, "id")
            for newFeatureChange, idx in self._compare_feature_changes(feature, oldFeature).values(): # Make the commit
                layer.changeAttributeValue(fid, idx, newFeatureChange)
            layer.changeAttributeValue(fid, layer.fields().indexFromName("id"), featureId) # Since ID cannot be changed, change it back to the original
            layer.changeGeometry(fid, feature.geometry()) # Update geometry

        # Looping through deletes
        for _, oldFeature, _ in self.failDelete:
            layer.addFeature(oldFeature)

        self.failAdd, self.failEdit, self.failDelete = [], [], []

    def on_before_commit_changes(self, layer):
        """
        Signal sent by QGIS when the save button is clicked on Attribute table or commitChanges() is called.
        Runs before the changes are committed to the data provider.
        For detailed workflow, see (../docs/commit-changes-workflow.md)
        
        Steps:
            1. Check field validity
            2. Gathers Edits, Deletes and Creates.
            3. Rollback Changes
            4. Commit changes to Feature Service
            5. Apply Updates to QGIS
            5. Handle Error
        """
        # ----------------- Progress Bar and Logger Setup ----------------- #
        progress = ProgressIterator( # Setup Progress Bar
            msg="Validating Changes...", window_title="Committing Changes",
            setCancelButtonNone=True, disableCloseButton=True, alwaysOnTop=False
        )
        progress.show()
        QApplication.processEvents()

        self.logger.QLogInfo("{} Committing Changes {}".format('-'*10, '-'*10)) # Setup Logger

        # ----------------- Check field validity ----------------- #
        self._check_field_validity()

        # ----------------- Gathers Edits, Deletes and Creates ----------------- #
        addCommit, editCommit, deleteCommit = self._consolidate_changes(layer)

        # ----------------- Update progress bar ----------------- #
        noOfCommits = len(addCommit) + len(editCommit) + len(deleteCommit)
        # Max Progress = Total number of commits + 3
        # +1 is for the progress.next statements used in the commit process outside of commiting the features.
        #   Namely, "Applying updates to QGIS...", 
        max_progress = noOfCommits + 1
        progress.set_maximum(max_progress)

        # ---------------------- Rollback Changes ---------------------- #
        layer.editBuffer().rollBack()

        # ---------------------- Commit changes to Feature Service ---------------------- #
        self.failAdd, self.failEdit, self.failDelete = self._commit_changes(layer, addCommit, editCommit, deleteCommit, progress)

        # ---------------------- Handle Updates ---------------------- #
        progress.next("Applying updates to QGIS...")
        self._apply_updates(layer)

        # ---------------------- Handle Error ---------------------- #
        progress.close()
        self._handle_errors(layer, self.failAdd, self.failEdit, self.failDelete)

    def _check_field_validity(self):
        """Check validity of fields. Throw Error if not valid."""
        # Check if all fields are valid (when edits happen, fields can become invalid)
        areAllFieldsValid = True
        if len(self.areFieldsValid) > 0:
            for v in self.areFieldsValid.values():
                areAllFieldsValid &= v

        # areAllFieldsValid is an instance variable used in methods like on_features_added
        # Ensures that Field validation is successful.
        if not areAllFieldsValid:
            self.dialogBox.QMessageCrit(
                title="Field validation failed", 
                text="Some fields you provided are not valid. Please correct them before saving the feature.",
                detailedText="Some fields you provided are not valid. See Logs for more details.")
            return False
        return True

    def _get_changes(self, layer):
        """ Gather Creates, Edits and Deletes"""
        editBuffer = layer.editBuffer()
        deletes = editBuffer.deletedFeatureIds()
        adds = editBuffer.addedFeatures()

        # Determine changed features.
        edits = set()
        for fid in editBuffer.changedGeometries():
            edits.add(fid)
        for fid in editBuffer.changedAttributeValues():
            edits.add(fid)
        for fid in deletes:
            edits.discard(fid)
        
        return adds, edits, deletes

    def _consolidate_changes(self, layer):
        """
        Consolidate changes and return a list of changes to be committed.

        Steps:
            1. Gather edits, deletes and creates
            2. Prepare exporter to export features to GeoJSON
            3. Loop through changes and add store them in respective commit list 
        """

        # ----------------- Gather edits, deletes and creates ----------------- #
        adds, edits, deletes = self._get_changes(layer)

        # ---------------------- Loop through changes and add store them in respective commit list ---------------------- #
        addCommit, editCommit, deleteCommit = [], [], []
        # Loop through Creates
        for fid in adds:
            self.update_ids(layer, layer.getFeature(fid))
            feature = layer.getFeature(fid)
            exporter = self._get_feature_exporter(layer, feature) # Feature exporter
            featureJson = self._export_feature(exporter, feature, self._get_feature_attribute(feature, "id")) # Export feature to GeoJSON
            addCommit.append((fid, feature, featureJson))

        # Loop through Edits
        for fid in edits:
            # self.update_ids(layer, layer.getFeature(fid))
            feature = layer.getFeature(fid)
            exporter = self._get_feature_exporter(layer, feature) # Feature exporter
            key = layer.name() + ":" + str(fid)

            # If ID is a change, take that ID, else take the newly added id
            if fid > 0 and key in self.id_map: 
                temp_id = self.id_map[key]
                featureJson = self._export_feature(exporter, feature, temp_id) # Export feature to GeoJSON
                oldFeature = next(layer.dataProvider().getFeatures(QgsFeatureRequest().setFilterFid(fid)))
                editCommit.append((fid, temp_id, feature, oldFeature, featureJson))
            else: 
                adds[fid] = None # Remove ID from adds, to not double count, if the change is an add
                featureJson = self._export_feature(exporter, feature, self._get_feature_attribute(feature, "id")) # Export feature to GeoJSON
                addCommit.append((fid, feature, featureJson)) # Add it to the add list
        
        # Loop through Deletes
        for fid in deletes:
            wid = self.id_map[layer.name() + ":" + str(fid)]
            oldFeature = next(layer.dataProvider().getFeatures(QgsFeatureRequest().setFilterFid(fid)))
            deleteCommit.append((fid, wid, oldFeature))

        return addCommit, editCommit, deleteCommit

    def _compare_feature_changes(self, newFeature, oldFeature):
        """Compares the changes made to a feature
        Returns a dictionary of the changes made to the feature
        """
        changes = {}
        for i,field in enumerate(newFeature.fields()):
            if self._get_feature_attribute(newFeature, field.name()) != self._get_feature_attribute(oldFeature, field.name()):
                changes[field.name()] = (self._get_feature_attribute(newFeature, field.name()), i)
        return changes

    def _commit_changes(self, layer, addCommit, editCommit, deleteCommit, progress):
        """
        Handles commits to the Feature Service.

        Note: 
            1. Doesn't stop if a request is not successful. Moves on to the next request.
            2. All requests are independent of each other and can occur in any order.
            This is because saving can only happen in one feature class at a time, due to QGIS restrictions
            3. Used PUT in case of Patch as well, since QGIS returns the full feature, and not just the edited parts.
        """

        collectionName = self.layerName_collectionName_map[layer.name()]
        failAdd, failEdit, failDelete = [], [], []

        layer.startEditing()

        # ---------------------- Commit changes to Feature Service ---------------------- #
        # Looping through creates
        for fid, feature, body_str in addCommit:
            commit_url = Constants.API_Paths.CREATE.format(base=self.features_url, collectionId=collectionName)
            resp = self.requestHandler.post_request(url=commit_url, body=body_str)
            progress.next("Saving: Creating new features...")
            if resp["success"]: 
                featureId = resp['response'].json()['id']
                feature.setAttribute('id', featureId)
                layer.addFeature(feature) # Make the commit
            else:
                failAdd.append((fid, feature, resp)) # Add to list of failed commits
                
        # Looping through edits
        for fid, featureId, feature, oldFeature, body_str in editCommit:
            commit_url = Constants.API_Paths.PUT.format(base=self.features_url, collectionId=collectionName, featureId=featureId)
            resp = self.requestHandler.put_request(url=commit_url, body=body_str)
            progress.next("Saving: Editing features...")
            if resp["success"]:
                for newFeatureChange, idx in self._compare_feature_changes(feature, oldFeature).values(): # Make the commit
                    layer.changeAttributeValue(fid, idx, newFeatureChange)
                layer.changeAttributeValue(fid, layer.fields().indexFromName("id"), featureId) # Since ID cannot be changed, change it back to the original
                layer.changeGeometry(fid, feature.geometry()) # Update geometry
            else:
                failEdit.append((fid, (feature, oldFeature), resp))

        # Looping through deletes
        for fid, featureId, oldFeature in deleteCommit:
            commit_url = Constants.API_Paths.DELETE.format(base=self.features_url, collectionId=collectionName, featureId=featureId)
            resp = self.requestHandler.delete_request(url=commit_url)
            progress.next("Saving: Deleting features...")
            if resp["success"]:
                self.internalDelete = True # Mark delete as internal, to skip function
                layer.deleteFeature(fid)
            else:
                failDelete.append((fid, oldFeature, resp))

        self.logger.QLogInfo("Report for Changes.\tAdds: {}\tEdits: {}\tDeletes: {}".format(len(addCommit), len(editCommit), len(deleteCommit)))
        self.logger.QLogInfo("          Failures.\tAdds: {}\tEdits: {}\tDeletes: {}".format(len(failAdd), len(failEdit), len(failDelete)))

        return failAdd, failEdit, failDelete

    def _apply_updates(self, layer):
        """Handle changes to other fields, if any, due to the creates and edits"""

        successAdd, successEdit, _ = self._get_changes(layer)
            
        # Update the floor field if it exists, for all successful creates and edits
        floor_index = layer.dataProvider().fieldNameIndex("floor")
        if floor_index != -1:
            self.update_floors(successAdd, layer, floor_index)
            self.update_floors(successEdit, layer, floor_index)

        # (if modified) Update the layer group name w/ updated facility layer
        self._update_layer_group_name(layer)

    def _handle_errors(self, layer, failAdd, failEdit, failDelete):
        """
        Handles the errors from the Feature Service
        """
        # If any errors, display all of them appropriately
        if (len(failAdd)+len(failDelete)+len(failEdit)>0):
            self.logger.writeErrorLogChanges([r['response'] for _, _, r in failAdd + failEdit + failDelete])
            error_list = ["Add Failed \t Feature name: {} \t Details: {}".format(self._get_feature_attribute(feature, "name"), resp["error_text"]) for (_, feature, resp) in failAdd] + \
                        ["Edit Failed \t FeatureId: {} \t Feature name: {} \t Details: {}".format(self._get_feature_attribute(feature, "id"), self._get_feature_attribute(feature, "name"), resp["error_text"]) 
                            for (_, (feature, _), resp) in failEdit] + \
                        ["Delete Failed \t FeatureId: {} \t Feature name: {} \t Details: {}".format(self._get_feature_attribute(feature, "id"), self._get_feature_attribute(feature, "name"), resp["error_text"]) 
                         for (_, feature, resp) in failDelete]
            self.dialogBox.QMessageCrit(
                title="Save Failed!",
                text="""Some or all of your saves to {} layer have failed!<br/>
Your changes are still present in QGIS. Please fix the issues and try saving again.<br/>
Logs can be found here: <a href='{}'>{}</a>""".format(layer.name(), self.logger.errorLogFilePath, self.logger.errorLogFileName),
                detailedText='\n'.join(error_list),
                width = 500, height = 500
            )
            self._handle_error_msgBar(layer.name(), is_fail=True)
        else:
            self.dialogBox.QMessageInfo(
                title="Save Successful!",
                text="Changes in {} layer saved successfully!".format(layer.name())
            )
            self._handle_error_msgBar(layer.name(), is_fail=False)
        return

    def _get_feature_exporter(self, layer, feature):
        """
        Prepare Exporter to export features to GeoJSON. Needed while adding/changing feature
        https://qgis.org/pyqgis/3.8/core/QgsJsonExporter.html
        """
        exporter = QgsJsonExporter(layer, 7)
        collectionName = self.layerName_collectionName_map[layer.name()]
        collection_definition = self.collectionName_collectionDef_map[collectionName] # Get collection definition
        attributeList = [attr["name"] for attr in collection_definition.get("properties", [])] # Get list of attributes
        includedList = []
        # Only add features that were populated by user and are in the definition 
        # (Since we can't make new attributes using Features service)
        for attr in attributeList:
            index = feature.fieldNameIndex(attr)
            if index != -1:
                includedList.append(index)
        exporter.setAttributes(includedList)

        return exporter

    def _export_feature(self, exporter, feature, input_id):
        """Export feature to GeoJSON"""
        # https://qgis.org/pyqgis/3.8/core/QgsJsonExporter.html
        featureJson = json.loads(exporter.exportFeature(feature, {}, input_id))
        featureJson.pop("bbox", None) # Remove bbox property, to not cause unexpected issues in service later
        return json.dumps(featureJson)

    def update_ids(self, layer, feature):
        collectionName = self.layerName_collectionName_map[layer.name()]
        referential_integrity_map = self.collectionName_referential_integrity_map[collectionName]
        for ref_field_name, ref_field_id in referential_integrity_map.items():
            field_index = self._get_feature_field_index(feature, ref_field_id)
            layer.changeAttributeValue(
                feature.id(),
                field_index,
                self._get_feature_attribute(feature, ref_field_name),
            )

    def update_floors(self, fids, layer, floor_index):
        for fid in fids: # Loop through all features
            feature = layer.getFeature(fid)
            levelId, unitId, featureId, ordinal = self._get_feature_attributes(feature, ["levelId", "unitId", "id", "ordinal"])
            """unitId, levelId, and ordinal are mutually exclusive
            unitId is used for Facility_2 ontology, in pointElement, lineElement, areaElement feature classes
            levelId is used for all feature classes in CustomOntology and Facility_2, except level and facility
            ordinal is used for level feature class 
            """
            if unitId != None and self.ontology == Constants.Ontology.FACILITY_2: # Update floor using unitId, only for Facility_2 ontology
                floor = self.unitId_ordinal_map[unitId]
                layer.changeAttributeValue(fid, floor_index, str(floor))
            elif levelId != None: # Update floor using levelId
                floor = self.levelId_ordinal_map[levelId]
                layer.changeAttributeValue(fid, floor_index, str(floor))
            elif ordinal: # Update floor using ordinal
                layer.changeAttributeValue(fid, floor_index, str(ordinal))
                # This means changes to level layer has been made, need to update floor-picker
                # If it is a change, first delete the ordinal related to the ID from the floor picker
                if featureId in self.levelId_ordinal_map:
                    del_ordinal = self.levelId_ordinal_map[featureId]
                    self.level_picker.remove(del_ordinal)
                    del self.ordinal_levelId_map[del_ordinal]
                # Update layer picker with latest floor information. Handles repeat cases and sorted updates of floor numbers
                for innerFeature in layer.getFeatures():
                    self.level_picker.append(self._get_feature_attribute(innerFeature, "ordinal"))
                # Update mappings
                self.levelId_ordinal_map[featureId] = ordinal
                self.ordinal_levelId_map[ordinal] = featureId
            self.refresh_floor_picker()

    def _set_widget_layer_id(self, layer_object, enum_name):
        enum_layer_id = self.enum_ids[enum_name]
        if enum_layer_id:
            layer_object.editFormConfig().setWidgetConfig(
                enum_name, {"Layer": enum_layer_id}
            )
    
    def _qgis_value_converter(self, qgis_value):
        """
        Converts QGIS multi-select string to array of strings
        Ex.'NULL' => None, "{ 'left, 'center', 'right' }" => ['left', 'center', 'right']
        """
        qgis_value = qgis_value.strip() # Remove leading and trailing spaces
        if not isinstance(qgis_value, str): # Continue if not string
            return qgis_value 
        if qgis_value == "NULL": # Null value
            return None 
        if not qgis_value.startswith("{") or not qgis_value.endswith("}"): # If not array
            return qgis_value
        
        qgis_value_split = qgis_value[1:-1].split(",") # Remove brackets and split by comma, to make array
        qgis_value_list = [s.strip() for s in qgis_value_split if s.strip()] # Remove spaces, empty strings
        if not qgis_value_list: 
            return [] # If no elements, empty array
        return qgis_value

    def _qgis_values_resolver(self, qgis_str):
        """Converts QGIS string into a valid JSON string"""
        json_obj = json.loads(qgis_str)
        json_props = json_obj.get("properties", {})
        json_obj["properties"] = dict(
            map(lambda item: (item[0], self._qgis_value_converter(item[1])), json_props.items())
        )
        # Remove entries with None value to reduce payload
        json_obj["properties"] = { k: v for k, v in json_obj["properties"].items() 
                                  if v is not None}

        # Handle obstruction area
        if "isObstruction" in json_obj["properties"]:
            if json_obj["geometry"]["type"] == "LineString":
                # For LineString, add a small buffer to construct a polygon as obstructionArea
                json_obj["properties"]["obstructionArea"] = (
                    mapping(shape(json_obj["geometry"]).buffer(0.000001))
                    if json_obj["properties"]["isObstruction"]
                    else None
                )
            elif json_obj["geometry"]["type"] == "Polygon":
                # For Polygon, the geometry itself as obstructionArea
                json_obj["properties"]["obstructionArea"] = (
                    json_obj["geometry"]
                    if json_obj["properties"]["isObstruction"]
                    else None
                )

        # Return stringified JSON object
        return json.dumps(json_obj)

    # Initializes level picker at the toolbar
    def _configure_level_picker(self):
        if hasattr(self, "toolbar_level_picker"):
            return
        self.toolbar_level_picker = QComboBox(self.iface.mainWindow())
        self.toolbar_level_picker.setToolTip("Azure Maps Creator Level Control")
        self.toolbar_level_picker.currentIndexChanged.connect(self.floor_picker_changed)
        self.toolbar_level_combobox_action = self.pluginToolBar.addWidget(
            self.toolbar_level_picker
        )
        self.level_picker = LevelPicker(
            [self.toolbar_level_picker]
        )

    def _open_welcome_message(self):
        self.dialogBox.QMessage(icon=QPixmap(":/plugins/azure_maps/media/icon-circle.png"),
                                isPixMapIcon=True,
                                text="Welcome to the Azure Maps Creator Plugin!",
                                informativeText='<a href="https://aka.ms/am-qgis-plugin">Azure Maps Creator Plugin Documentation</a>',
                                title="Azure Maps Creator",
                                windowFlags=Qt.WindowStaysOnTopHint)
        
    def _open_deprecation_message(self):
        self.dialogBox.QMessageCrit(
            title="Azure Maps Creator Retirement",
            text='The Azure Maps Creator indoor map service is now deprecated and will be retired on 9/30/25.<br/>For more information, see <a href="https://aka.ms/AzureMapsCreatorDeprecation">End of Life Announcement of Azure Maps Creator</a>.',
            detailedText='The Azure Maps Creator indoor map service is now deprecated and will be retired on 9/30/25. For more information, see https://aka.ms/AzureMapsCreatorDeprecation.',
            windowFlags=Qt.WindowStaysOnTopHint,
            minSize=800
        )
        self.msgBar.QMessageBarCrit(
            title="Azure Maps Creator Retirement",
            text="The Azure Maps Creator indoor map service is now deprecated and will be retired on 9/30/25. For more information, see https://aka.ms/AzureMapsCreatorDeprecation.",
        )

    def _getFeaturesButton_setEnabled(self, boolean):
        self.dlg.getFeaturesButton.setEnabled(boolean)

    def hideGroup(self, group):
        if isinstance(group, QgsLayerTreeGroup):
            self.hideNode(group)
        elif isinstance(group, (str, unicode)):
            self.hideGroup(self.root.findGroup(group))

    def hideNode(self, node, bHide=True):
        if type(node) in (QgsLayerTreeLayer, QgsLayerTreeGroup):
            index = self.model.node2index(node)
            self.ltv.setRowHidden(index.row(), index.parent(), bHide)
            node.setCustomProperty("nodeHidden", "true" if bHide else "false")
            self.ltv.setCurrentIndex(self.model.node2index(self.root))

    def hideLayer(self, mapLayer):
        if isinstance(mapLayer, QgsMapLayer):
            self.hideNode(self.root.findLayer(mapLayer.id()))

    def _on_layer_removed(self, node, indexFrom, indexTo):
        # BUG: This is not working as expected
        pass
        # if node == self.base_group:
        #     self.level_picker.clear()

    def _update_layer_group_name(self, facility_layer):
        dataset_id = self.current_dataset_id
        if (
            facility_layer is None
            or not callable(getattr(facility_layer, "name", None))
            or facility_layer.name() != "facility"
        ):
            return
        features = list(facility_layer.getFeatures())
        facility_count = len(features)
        if facility_count > 1:
            self.base_group.setName(
                str(facility_count) + " Facilities | " + str(dataset_id)
            )
        elif facility_count == 1:
            facility_name = features[0]["name"]
            facility_name = (
                facility_name
                if facility_name != NULL and facility_name != ""
                else features[0]["id"]
            )
            self.base_group.setName(str(facility_name) + " | " + str(dataset_id))
        else:
            self.base_group.setName(str(dataset_id))

def get_depth(collection_name, references):
    ref_list = references.get(collection_name, None)
    if not ref_list:
        return 0
    return 1 + max(get_depth(key, references) for (key, _) in ref_list)