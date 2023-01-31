# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AzureMapsPluginDialog
                                 A QGIS plugin
 Azure Maps plugin for QGIS 3
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-06-04
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Microsoft Corporation
        email                : bjapark@microsoft.com, xubin.zhuge@microsoft.com
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

import os
import webbrowser

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from qgis.core import *

from .Constants import Constants

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "azure_maps_plugin_dialog_base.ui")
)


class AzureMapsPluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(AzureMapsPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface

        self.getFeaturesButton.clicked.connect(self.on_get_features_clicked)
        self.getFeaturesButton_2.clicked.connect(self.on_get_features_clicked)
        self.currentExtentButton.clicked.connect(self.on_current_extent_clicked)
        self.allExtentButton.clicked.connect(self.on_all_extent_clicked)
        # self.adButton.clicked.connect(self.on_ad_button_clicked)
        # self.skButton.clicked.connect(self.on_sk_button_clicked)
        # self.manualADButton.clicked.connect(self.on_manual_ad_button_clicked)
        # self.appIdHelpButton.clicked.connect(self.on_appid_help_button_clicked)

        config_path = (
            QgsApplication.qgisSettingsDirPath().replace("\\", "/")
            + Constants.Paths.RELATIVE_CONFIG_PATH
        )
        self.plugin_settings = QSettings(config_path, QSettings.IniFormat)

        # Creator
        self.datasetId.setText(self.plugin_settings.value("datasetId", ""))

        # Auth
        # self.tenant.setText(self.plugin_settings.value("tenant", ""))
        # self.appId.setText(self.plugin_settings.value("appId", ""))
        # self.clientId.setText(self.plugin_settings.value("clientId", ""))
        self.sharedKey.setText(self.plugin_settings.value("sharedKey", ""))
        # self.manualClientId.setText(self.plugin_settings.value("manualClientId", ""))
        # self.bearerToken.setPlainText(self.plugin_settings.value("bearerToken", ""))

        # if bool(self.plugin_settings.value("useSharedKey", True)):
        # self.skButton.setChecked(True)
        # else:
        # self.adButton.setChecked(True)

    def saveSettings(self):
        # Creator
        self.plugin_settings.setValue("datasetId", self.datasetId.text())

        # Auth
        # self.plugin_settings.setValue("tenant", self.tenant.text())
        # self.plugin_settings.setValue("appId", self.appId.text())
        # self.plugin_settings.setValue("clientId", self.clientId.text())
        # self.plugin_settings.setValue("useSharedKey", self.skButton.isChecked())
        self.plugin_settings.setValue("sharedKey", self.sharedKey.text())
        # self.plugin_settings.setValue("manualClientId", self.manualClientId.text())
        # self.plugin_settings.setValue("bearerToken", self.bearerToken.toPlainText())

    def on_get_features_clicked(self):
        self.saveSettings()

    def on_current_extent_clicked(self):

        # Get the extent, in map canvas CRS.
        canvas = self.iface.mapCanvas()
        extent = canvas.extent()

        # Extract corners and edges.
        xmin = extent.xMinimum()
        ymin = extent.yMinimum()
        xmax = extent.xMaximum()
        ymax = extent.yMaximum()
        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) / 2

        # Create transform from canvas CRS to WGS84.
        from_crs = canvas.mapSettings().destinationCrs()
        to_crs = QgsCoordinateReferenceSystem(4326)
        transform = QgsCoordinateTransform(from_crs, to_crs, QgsProject.instance())

        # Create WGS84 extent from two corners.
        mins = transform.transform(xmin, ymin)
        maxs = transform.transform(xmax, ymax)
        extent = QgsRectangle(mins, maxs)

        # Expand to include other corners and four edge midpoints.
        extent.include(transform.transform(xmin, ymax))
        extent.include(transform.transform(xmax, ymin))
        extent.include(transform.transform(xmid, ymin))
        extent.include(transform.transform(xmid, ymax))
        extent.include(transform.transform(xmin, ymid))
        extent.include(transform.transform(xmax, ymid))

        # Round and assign to input widgets.
        dp = 7
        self.extentWest.setText(str(round(extent.xMinimum(), dp)))
        self.extentSouth.setText(str(round(extent.yMinimum(), dp)))
        self.extentEast.setText(str(round(extent.xMaximum(), dp)))
        self.extentNorth.setText(str(round(extent.yMaximum(), dp)))

    def on_all_extent_clicked(self):
        self.extentNorth.setText("")
        self.extentSouth.setText("")
        self.extentEast.setText("")
        self.extentWest.setText("")

    def on_ad_button_clicked(self):
        self.adFrame.setEnabled(True)
        self.sharedKey.setEnabled(False)
        self.manualADFrame.setEnabled(False)

    def on_sk_button_clicked(self):
        self.adFrame.setEnabled(False)
        self.sharedKey.setEnabled(True)
        self.manualADFrame.setEnabled(False)

    def on_manual_ad_button_clicked(self):
        self.adFrame.setEnabled(False)
        self.sharedKey.setEnabled(False)
        self.manualADFrame.setEnabled(True)

    def on_appid_help_button_clicked(self):
        webbrowser.open("https://go.microsoft.com/fwlink/?linkid=2099115&clcid=0x409")
