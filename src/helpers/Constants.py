from ..models.Facility_2 import Facility_2
class Constants(Facility_2):
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

    class API_Versions:
        V20 = "2.0"
        V20220901PREVIEW = "2022-09-01-preview"

    WFS  = "wfs"
    FEATURES = "features"
    AZURE_MAPS = "Azure Maps"

    CRS_WGS84 = "EPSG:3857"

