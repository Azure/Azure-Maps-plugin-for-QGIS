from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *

class AzureMapsPluginMessageBar:

    def __init__(self, iface, logger):
        self.iface = iface
        self.msgBar = self.iface.messageBar()
        self.logger = logger
        self.item_map = {} # Dictionary to store items in the message bar. Useful to pop specific items.

    def set_parameters(self, logger):
        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def get_bar(self):
        """Return the message bar."""
        return self.msgBar
    
    def reset_item_map(self):
        """Reset the item map."""
        self.item_map = {}

    def pushMessage(
        self, level, text,
        title=None, showMore=None, duration=-1,
        item_id=None, **kwargs
    ):
        """
        Custom QGIS Message Bar. Returns the item containing message that was created, if successful.
        Store the item in a dictionary with the item_id as the key.
        """
        try:
            self.msgBar.pushMessage(
                title=title,
                text=text,
                showMore=showMore,
                level=level,
                duration=duration
            )
            item = self.msgBar.currentItem()
            if item_id:
                self.item_map[item_id] = item
            return item
        except Exception as e:
            self.logger.debug("Error pushing message to message bar: {}".format(e))
            return None

    def pop(self, item=None, item_id=None, **kwargs):
        """
        Pop a message from the message bar. Returns the item that was popped, if successful.
        If item_id is specified, pop the item with that id. If item is specified, pop that item.
        If neither item_id nor item is specified, pop the last item.

        If user closes widget manually, there is no way to know what widgets theiy closed.
        Hence, if pop fails, we ignore the error.
        """
        try:
            if item:
                self.msgBar.popWidget(item)
                return item
            elif item_id:
                item = self.item_map.get(item_id, None)
                if item:
                    self.msgBar.popWidget(item)
                    del self.item_map[item_id]
                    return item
            else:
                return self.msgBar.popWidget()
        except Exception as e:
            return None
    
    def clear(self):
        """Clear all messages from the message bar."""
        return self.msgBar.clearWidgets()
    
    def currentItem(self):
        """Return the current message in the message bar."""
        return self.msgBar.currentItem()

    def get_item(self, item_id):
        """Return the item with the given id."""
        return self.item_map.get(item_id, None)
    
    def items(self):
        """Return all messages in the message bar."""
        return self.msgBar.items()
    
    def pushItem(self, item):
        """Push a message to the message bar. Returns the item containing message that was pushed, if successful."""
        self.msgBar.pushItem(item)
        item = self.msgBar.currentItem()
        return item
    
    def pop_push_message(self, **kwargs):
        """Pop and push a message"""
        self.pop(**kwargs)
        return self.pushMessage(**kwargs)
    
    def QMessageBarInfo(self, **kwargs): 
        """Informational Messages"""
        return self.pushMessage(level=Qgis.Info, **kwargs)
    
    def QMessageBarWarn(self, **kwargs): 
        """Warning Messages"""
        return self.pushMessage(level=Qgis.Warning, **kwargs)
    
    def QMessageBarCrit(self, **kwargs): 
        """Critical Messages"""
        return self.pushMessage(level=Qgis.Critical, **kwargs)

    def QMessageBarSuccess(self, **kwargs): 
        """Critical Messages"""
        return self.pushMessage(level=Qgis.Success, **kwargs)
    
    def QMessageBarPopPushInfo(self, **kwargs):
        """Pop last message and add an informational message"""
        return self.pop_push_message(level=Qgis.Info, **kwargs)
    
    def QMessageBarPopPushWarn(self, **kwargs):
        """Pop last message and add a warning message"""
        return self.pop_push_message(level=Qgis.Warning, **kwargs)
    
    def QMessageBarPopPushCrit(self, **kwargs):
        """Pop last message and add a critical message"""
        return self.pop_push_message(level=Qgis.Critical, **kwargs)
    
    def QMessageBarPopPushSuccess(self, **kwargs):
        """Pop last message and add a success message"""
        return self.pop_push_message(level=Qgis.Success, **kwargs)

