"""
Custom Ontology Model
"""

class CUSTOM_ONTOLOGY:
    class COLLECTIONS:
        LVL = "level"
        FCL = "facility"
        nonEditableCollections = [LVL, FCL]

    class BASE_ATTR:
        azureMapsIntId = "azureMapsIntId"
        reservedProperties = ["azureMapsIntId"]
        hiddenProperties = reservedProperties

    class FCL(BASE_ATTR):
        name = "name"
        required_fields = []

    class LVL(BASE_ATTR):
        facilityId = "facilityId"
        ordinal = "ordinal"
        name = "name"
        required_fields = []
        
    class CUSTOM_COLLECTIONS(BASE_ATTR):
        name = "name"
        layerName = "layerName"
        levelId = "levelId"
        levelOrdinal = "levelOrdinal"
        required_fields = []