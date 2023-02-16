from qgis.core import *
import json 

class AzureMapsPluginLogger:

    def __init__(self, iface, hideSubscriptionKey=True, subscriptionKey=None, logFolder=None, dataset_id=None):
        self.iface = iface
        self.hideSubscriptionKey = hideSubscriptionKey
        self.subscriptionKey = subscriptionKey
        self.logFolder = logFolder
        self.dataset_id = dataset_id

    def setSubscriptionKey(self, subscriptionKey):
        self.subscriptionKey = subscriptionKey
    
    def setDatasetId(self, dataset_id):
        self.dataset_id = dataset_id
    
    def setLogFolder(self, logFolder):
        self.logFolder = logFolder
    
    def QLog(self, level, log_text, tag="Logs"):
        """Logging Method"""
        if type(log_text) == dict: log_text = json.dumps(log_text)
        if self.hideSubscriptionKey and self.subscriptionKey:
            sub_key_encoded = "subscription-key={}".format(self.subscriptionKey)
            sub_key_replace = "subscription-key=***{}".format(self.subscriptionKey[-3:])
            log_text = log_text.replace(sub_key_encoded, sub_key_replace)
        QgsMessageLog.logMessage(
                log_text,
                tag,
                level,
            )
    
    def QLogInfo(self, log_text): 
        """Informational Logs"""
        self.QLog(Qgis.Info, log_text)

    def QLogCrit(self, log_text): 
        """Critical Logs"""
        self.QLog(Qgis.Critical, log_text)

    def QLogWarn(self, log_text): 
        """Warning Logs"""
        self.QLog(Qgis.Warning, log_text)
