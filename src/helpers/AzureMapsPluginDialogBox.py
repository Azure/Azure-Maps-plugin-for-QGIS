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
        execute=True,
        width=None,
        height=None,
        isPixMapIcon=False
    ):
        """Custom QGIS Message Dialog Box"""
        
        # Standard Configuration
        msg = QMessageBox()
        if isPixMapIcon:
            msg.setIconPixmap(icon)
        else:
            msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setTextFormat(Qt.RichText)
        msg.setStandardButtons(buttons)
        msg.setDetailedText(detailedText)
        msg.setInformativeText(informativeText)
        msg.setWindowFlags(windowFlags)
        if windowTitle: msg.setWindowTitle(windowTitle)

        # Set minimum size - QMessageBox by default doesn't allow resizing default size
        layout = msg.layout()
        spacer = QSpacerItem(minSize, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())

        # Set definitie width and height, if specified.
        if width or height: 
            width_string = "width: {}px;".format(width) if width else None
            height_string = "height: {}px;".format(height) if height else None
            all_strings = [width_string, height_string]
            all_strings_valid = [s for s in all_strings if s]
            valid_str = '; '.join(all_strings_valid) # Format should be "QLabel{width: 500px; height: 500px; }"
            msg.setStyleSheet("QLabel{ " + valid_str + " }")

        if execute: return msg.exec()
        return msg
    
    def QMessageInfo(self, **kwargs): 
        """Informational Messages"""
        return self.QMessage(QMessageBox.Information, **kwargs)
    
    def QMessageWarn(self, **kwargs): 
        """Warning Messages"""
        return self.QMessage(QMessageBox.Warning, **kwargs)
    
    def QMessageCrit(self, **kwargs): 
        """Critical Messages"""
        return self.QMessage(QMessageBox.Critical, **kwargs)

    def QMessageQuestion(self, **kwargs): 
        """Critical Messages"""
        return self.QMessage(QMessageBox.Question, **kwargs)
