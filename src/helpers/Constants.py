from enum import Enum
from ..models.FACILITY_2 import FACILITY_2
from ..models.CUSTOM_ONTOLOGY import CUSTOM_ONTOLOGY
from ..models.ONTOLOGY import ONTOLOGY
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
class Constants:

    class Ontology(ONTOLOGY): pass
    class CustomOntology(CUSTOM_ONTOLOGY): pass
    class Facility_2(FACILITY_2): pass
    
    class Paths:
        RELATIVE_PLUGIN_PATH = "python/plugins/QGISPlugin"
        RELATIVE_CONFIG_PATH = "{}/plugin-config.ini".format(RELATIVE_PLUGIN_PATH)
        PLUGIN_CIRCLE_ICON = ":/plugins/azure_maps/media/icon-circle.png"

    class Logs:
        LOG_FOLDER_NAME = "AzureMaps_logs"
        ERROR_LOG_FOLDER_NAME = "AzureMaps_ErrorLogs"
        FAILURE = "Failure"
        SUCCESS = "Success"
        WARNING = "Warning"

    class Geography:
        US = "United States"
        EU = "Europe"
        TEST = "Test"
        LOCALHOST = "Localhost"

    class Host:
        US = "https://us.atlas.microsoft.com"
        EU = "https://eu.atlas.microsoft.com"
        US_TEST = "https://us.t-azmaps.azurelbs.com"
        DEFAULT = "https://atlas.microsoft.com"

    class API_Paths:
        BASE = "{host}/{apiName}/datasets/{datasetId}"
        CREATE = "{base}/collections/{collectionId}/items"
        DELETE = "{base}/collections/{collectionId}/items/{featureId}"
        GET = "{base}/collections/{collectionId}/items/{featureId}"
        GET_COLLECTION = "{base}/collections/{collectionId}"
        GET_COLLECTION_DEF = "{base}/collections/{collectionId}/definition"
        GET_COLLECTIONS = "{base}/collections"
        GET_ITEMS = "{base}/collections/{collectionId}/items"
        GET_LANDING_PAGE = "{base}"
        LIST_CONFORMANCE = "{base}/conformance"
        PATCH = "{base}/collections/{collectionId}/items/{featureId}"
        PUT = "{base}/collections/{collectionId}/items/{featureId}"

    class HTTPS:
        class Methods:
            PUT = "PUT"
            PATCH = "PATCH"
            GET = "GET"
            POST = "POST"
            DELETE = "DELETE"

        class Content_type:
            GEOJSON = "application/geo+json"
            PATCH_JSON = "application/merge-patch+json"

        MAX_RETRIES = 3
        RETRY_INTERVAL = 0.5 # 0.5 seconds
        GET_LIMIT = 500

    class API_Versions:
        V20 = "2.0"
        V20230301PREVIEW = "2023-03-01-preview"

    WFS  = "wfs"
    FEATURES = "features"
    AZURE_MAPS = "Azure Maps"
    AZURE_MAPS_PLUGIN_NAME = "QGISPlugin" # TODO: FINALIZE

    CRS_EPSG_3857 = "EPSG:3857" # Web Mercator
    CRS_EPSG_4326 = "EPSG:4326" # Mercator

    QGIS_VECTOR_LAYER_URI = '{geometryType}?crs={crs}&index=yes&{fieldString}'
    LAYER_NAME_DELIMITER = "-"

    class GEOMETRY_TYPE(Enum):
        """Geometry type constants."""
        POINT = "point"
        MULTIPOINT = "multipoint"
        LINESTRING = "linestring"
        MULTILINESTRING = "multilinestring"
        POLYGON = "polygon"
        MULTIPOLYGON = "multipolygon"
        NOGEOMETRY = "nogeometry"
        INVALID = "invalid"

        @classmethod
        def _missing_(cls, value):
            value = value.lower().strip()
            for member in cls:
                if member.value == value:
                    return member
            if value == "": return cls.NOGEOMETRY
            # BUG: Ignoring geometryCollection for now. FIX in other places too.
            if value == "geometrycollection": return cls.INVALID
            return cls.INVALID

        @classmethod
        def from_QgsWkbTypes(cls, wkb_type):
            """Converts a QgsWkbTypes to a geometry type constant."""
            if wkb_type == QgsWkbTypes.Point:
                return cls.POINT
            elif wkb_type == QgsWkbTypes.MultiPoint:
                return cls.MULTIPOINT
            elif wkb_type == QgsWkbTypes.LineString:
                return cls.LINESTRING
            elif wkb_type == QgsWkbTypes.MultiLineString:
                return cls.MULTILINESTRING
            elif wkb_type == QgsWkbTypes.Polygon:
                return cls.POLYGON
            elif wkb_type == QgsWkbTypes.MultiPolygon:
                return cls.MULTIPOLYGON
            elif wkb_type == QgsWkbTypes.NoGeometry:
                return cls.NOGEOMETRY
            else:
                return cls.NOGEOMETRY
            
        @classmethod
        def from_definition(cls, geometry_types):
            geometryTypes = []
            geometry_type_list = geometry_types.split(",")
            for g in geometry_type_list:
                try:
                    gType = g.lower().strip()
                    if gType == "":
                        geometryTypes.append(cls.NOGEOMETRY)
                    elif cls(gType) is not None:
                        geometryTypes.append(cls(gType))
                except ValueError as ve:
                    geometryTypes.append(cls.INVALID)
                    # raise Exception("Geometry type {} is not supported.".format(gType))
            return geometryTypes
        
        def __repr__(self) -> str:
            return self.name
        
        def __str__(self) -> str:
            return self.name
        
        def __format__(self, format_spec: str) -> str:
            return self.name

    class FIELD_TYPE:
        """Field type constants. These are used to make fields for QGIS layers."""
        STRING = "String(0,0)"
        DOUBLE = "Double(0,0)"
        STRINGLIST = "StringList(0,0)"
        BOOLEAN = "Boolean(1,0)"

        @classmethod
        def from_definition_type(cls, definition_type):
            """
            Converts a type defined in definition a field type constant.
            For JSON type:
                - If it's a featureId, it is connected to a different feature, but still a string
                -   "type": {
                        "featureId": "unit"
                    }   
                - If it's an array, it is a list of strings
                -   "type": {
                        "array": {
                            "featureId": "directoryInfo"
                        }
                    }
                - If it's a geometry, it is a string
                -   "type": {
                        "geometry": [
                            "Polygon",
                            "MultiPolygon"
                        ],
                        "isFragmented": false,
                        "srid": 4326
                    }
            """
            # Parse JSON definition type
            if type(definition_type) == dict:
                if "featureId" in definition_type: 
                    return cls.STRING
                elif "array" in definition_type:
                    return cls.STRINGLIST
                elif "geometry" in definition_type:
                    return cls.STRING
                return cls.STRING # Default to string
            else:
                # Only text, doulbe, and boolean are allower other than a json type
                if definition_type == "text":
                    return cls.STRING
                elif definition_type == "double" or definition_type == "double_precision":
                    return cls.DOUBLE
                elif definition_type == "boolean":
                    return cls.BOOLEAN
                return cls.STRING # Default to string

