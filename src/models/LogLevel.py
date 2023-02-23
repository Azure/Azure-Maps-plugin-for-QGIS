from enum import Enum

from qgis.core import *

class LogLevel(Enum):
    INFO = Qgis.Info
    WARNING = Qgis.Warning
    CRITICAL = Qgis.Critical
    SUCCESS = Qgis.Success

    def __str__(self):
        return self.name
