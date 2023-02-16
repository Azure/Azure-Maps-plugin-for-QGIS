from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *

class AzureMapsPluginDialogBox:

    def __init__(self, iface):
        self.iface = iface

    def QMessage(
        self,
        icon,
        title,
        text,
        buttons=QMessageBox.Ok,
        detailedText="",
        informativeText="",
        minSize=500,
        windowFlags=Qt.WindowStaysOnTopHint,
        windowTitle=None,
        execute=True
    ):
        """Custom QGIS Message Dialog Box"""
        
        # Standard Configuration
        msg = QMessageBox(icon, title, text)
        msg.setStandardButtons(buttons)
        msg.setDetailedText(detailedText)
        msg.setInformativeText(informativeText)
        msg.setWindowFlags(windowFlags)
        if windowTitle: msg.setWindowTitle(windowTitle)

        # Set minimum size - QMessageBox by default doesn't allow resizing default size
        layout = msg.layout()
        spacer = QSpacerItem(minSize, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())

        if execute: return msg.exec()
        return msg
    
    def QMessageInfo(self, title, text, informativeText="", detailedText="", buttons=QMessageBox.Ok): 
        """Informational Messages"""
        self.QMessage(QMessageBox.Information, title=title, text=text, 
        informativeText=informativeText, detailedText=detailedText, buttons=buttons)
    
    def QMessageWarn(self, title, text, informativeText="", detailedText="", buttons=QMessageBox.Ok): 
        """Warning Messages"""
        self.QMessage(QMessageBox.Warning, title=title, text=text, 
        informativeText=informativeText, detailedText=detailedText, buttons=buttons)
    
    def QMessageCrit(self, title, text, informativeText="", detailedText="", buttons=QMessageBox.Ok): 
        """Critical Messages"""
        self.QMessage(QMessageBox.Critical, title=title, text=text, 
        informativeText=informativeText, detailedText=detailedText, buttons=buttons)
