from qgis.core import *
import os, inspect
import json 
from datetime import datetime

from ..models.LogLevel import LogLevel
from .Constants import Constants

sb = 2 # Max spacing between columns
sb_str = " " * sb # String of spaces for max spacing between columns
sl = 8 # Max spacing for level column
ss = 7 # Max spacing for status column
st = 19 # Max spacing for time column

class AzureMapsPluginLogger:

    def __init__(self, iface, hideSubscriptionKey=True, subscription_key=None, 
                    dataset_id=None,        
                    autoLogToFile=True, logFolder=None, debugLog=False):
        self.iface = iface
        self.hideSubscriptionKey = hideSubscriptionKey # Hide subscription key in logs
        self.subscription_key = subscription_key # Azure Maps Subscription Key
        self.dataset_id = dataset_id # Azure Maps Dataset ID
        self.autoLogToFile = autoLogToFile # Boolean to enable automatically log to file
        self.logFolder = logFolder # Folder to save log files
        self.errorLogFolderName = Constants.Logs.ERROR_LOG_FOLDER_NAME # Folder to save error log files
        self.debugLog = debugLog # Boolean to enable debug log
        self.setupLogFile()
    
    def set_parameters(self, subscription_key=None, dataset_id=None, logFolder=None):
        """Set parameters"""
        if subscription_key: self.set_subscription_key(subscription_key)
        if dataset_id: self.setDatasetId(dataset_id)
        if logFolder: self.setLogFolder(logFolder)

    def setupLogFile(self):
        """Setup log file names and paths"""
        self.logFileName = self._generateLogFileName()
        self.logFilePath = None
        self.setLogFolder(self.logFolder)
        
    def _generateLogFileName(self):
        """Generate log file name based on timestamp"""
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M%S")
        return "AzureMaps_{}.log".format(dt_string)

    def _generateErrorLogFileName(self):
        """Generate error log file name based on timestamp"""
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M%S")
        return "AzureMaps_ErrorLog_{}.json".format(dt_string)

    def _generateLogDateTime(self):
        """Generate log date time string"""
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string

    def set_subscription_key(self, subscription_key):
        """Set subscription key"""
        self.subscription_key = subscription_key
    
    def setDatasetId(self, dataset_id):
        """Set dataset id"""
        self.dataset_id = dataset_id
    
    def setLogFolder(self, logFolder):
        """
        Set log folder path and create folder if it doesn't exist
        Set log file path variable
        Set error log folder path and create folder if it doesn't exist
        """
        self.logFolder = logFolder
        if self.logFolder:
            self.logFolderName = os.path.basename(self.logFolder)
            if not os.path.exists(self.logFolder):
                os.mkdir(self.logFolder)
            self.logFilePath = "{}/{}".format(self.logFolder, self.logFileName)
            self.errorLogFolderPath = "{}/{}".format(self.logFolder, self.errorLogFolderName)
            if not os.path.exists(self.errorLogFolderPath):
                os.mkdir(self.errorLogFolderPath)
    
    def _hide_subscription_key(self, log_text):
        """Hide subscription key in log text"""
        if self.hideSubscriptionKey and self.subscription_key:
            sub_key_encoded = "subscription-key={}".format(self.subscription_key)
            sub_key_replace = "subscription-key=***{}".format(self.subscription_key[-3:])
            log_text = log_text.replace(sub_key_encoded, sub_key_replace)
        return log_text

    def _print_frame_info(self, frame_info):
        filename = frame_info.filename.split(Constants.AZURE_MAPS_PLUGIN_NAME)[1]
        spacing = ' '*(st + sb + sl + sb + ss + sb)
        return "\n{}[{}:{}:{}]\t[code_context:{}]".format(spacing, filename, frame_info.function, frame_info.lineno, frame_info.code_context)
    
    def _add_debug_info(self, inspect_frame):
        """Add debug info to log text"""
        if self.debugLog and inspect_frame:
            info = inspect.getframeinfo(inspect_frame)
            return self._print_frame_info(info)
        return ""

    def _format_log_text(self, status_code=None, status=None, status_text=None, request_type=None, url=None, text=None, inspect_frame=None):
        """Format log text"""
        if type(status_text) == dict: status_text = json.dumps(status_text) # Convert status_text json to string
        # ss = spacing for status, sb_str = string for spacing between columns
        # defined at the top of this file. ss calculated based on the max length of the status code
        log_text_format = "{:<{ss}}{sb_str}{}" 

        if request_type and url: # Request logs
            log_text = log_text_format.format(request_type, url, ss=ss, sb_str=sb_str)
        elif status_code and status_text: # Response logs with status code
            log_text = log_text_format.format(status_code, status_text, ss=ss, sb_str=sb_str)
        elif status and status_text: # Response logs with status
            log_text = log_text_format.format(status, status_text, ss=ss, sb_str=sb_str)
        elif text: # General logs
            log_text = log_text_format.format("", text, ss=ss, sb_str=sb_str)
        else: # Invalid log 
            raise Exception("Invalid log text parameters")
        log_text = self._hide_subscription_key(log_text)
        log_text += self._add_debug_info(inspect_frame)
        return log_text

    def QLog(self, level, tag="Logs", **kwargs):
        """Logging Method"""
        log_text = self._format_log_text(**kwargs)
        QgsMessageLog.logMessage(
                log_text,
                tag,
                level,
            )
        if self.autoLogToFile:
            self.writeLog(level, log_text)
    
    def QLogDebug(self, text=None, **kwargs):
        """Debug Logs"""
        if self.debugLog:
            self.QLog(Qgis.Info, text=text, **kwargs)

    def QLogInfo(self, text=None, **kwargs): 
        """Informational Logs"""
        self.QLog(Qgis.Info, text=text, **kwargs)

    def QLogCrit(self, text=None, **kwargs): 
        """Critical Logs"""
        self.QLog(Qgis.Critical, text=text, **kwargs)

    def QLogWarn(self, text=None, **kwargs): 
        """Warning Logs"""
        self.QLog(Qgis.Warning, text=text, **kwargs)

    def writeLog(self, level, log_text, logFile=None):
        """Write log to file"""
        log_text = "{:<{sl}}{sb_str}{}".format(LogLevel(level), log_text, sl=sl, sb_str=sb_str)
        if not logFile: logFile = self.logFilePath
        if logFile:
            with open(logFile, "a") as f:
                f.write("{}{sb_str}{}\n".format(self._generateLogDateTime(), log_text, sb_str=sb_str))

    def responseToJSON(self, response):
        """Convert response to JSON for logging"""
        body = None
        if response.request.body:
            body = json.loads(response.request.body)
        return {
            'request': {
                'url': self._hide_subscription_key(response.request.url),
                'method': response.request.method,
                'headers': dict(response.request.headers),
                'body': body,
            },
            'response': response.json()
        }
    
    def writeErrorLog(self, json_response, errorLogFilePath=None):
        """Write error logs to file"""
        if not errorLogFilePath: 
            self.errorLogFileName = self._generateErrorLogFileName()
            self.errorLogFilePath = "{}/{}".format(self.errorLogFolderPath, self.errorLogFileName)
        with open(self.errorLogFilePath, "w") as f:
            json.dump(json_response, f, indent=2)
        # Log error log file path
        self.QLogInfo(status="Failure", status_text="Error log written to {}".format(self.errorLogFilePath))
        
    def writeErrorLogChanges(self, responseList):
        """
        Write error logs to file for all changes
        All error responses for changes are combined into one JSON file, per commit session
        """
        self.writeErrorLog([self.responseToJSON(response) for response in responseList])