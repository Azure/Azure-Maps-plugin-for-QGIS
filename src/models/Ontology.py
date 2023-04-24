from enum import Enum

class ONTOLOGY:
    FACILITY_1 = 'facility-1.0'
    FACILITY_2 = 'facility-2.0'
    CUSTOM = 'custom'
    NOONTOLOGY = 'noontology'
    UNKNOWN = 'unknown'
        
    @classmethod
    def get_display_order(cls, ontology, collections):
        collectionNames = [c["id"] for c in collections]
        collectionNames_lower = [c.lower().strip() for c in collectionNames]
        if ontology == cls.FACILITY_1:
            return [
                "category",
                "directoryInfo",
                "pointElement",
                "verticalPenetration",
                "zone",
                "lineElement",
                "areaElement",
                "opening",
                "unit",
                "level",
                "facility",
            ]
        elif ontology == cls.FACILITY_2:
            defined_collection_order = [
                "category",
                "directoryInfo",
                "pointElement",
                "verticalPenetration",
                "zone",
                "lineElement",
                "structure",
                "areaElement",
                "opening",
                "unit",
                "level",
                "facility",
            ]
            defined_collection_order_lower = [c.lower().strip() for c in defined_collection_order]
            other_collections = [c for c in collectionNames if c.lower().strip() not in defined_collection_order_lower]
            return defined_collection_order + other_collections
        elif ontology == cls.CUSTOM: # Includes NoOntology, hence only using collectionNames if present in collections
            pre_defined_collection_order = [
                "level",
                "facility",
            ]
            defined_collection_order = [c for c in pre_defined_collection_order if c.lower().strip() in collectionNames_lower] # Only include if collectionName is in collections
            defined_collection_order_lower = [c.lower().strip() for c in defined_collection_order]
            other_collections = [c for c in collectionNames if c.lower().strip() not in defined_collection_order_lower]
            return other_collections + defined_collection_order
        else:
            return []
        
    @classmethod
    def get_loading_order(cls, ontology, collections):
        collectionNames = [c["id"] for c in collections]
        collectionNames_lower = [c.lower().strip() for c in collectionNames]
        if ontology == cls.FACILITY_1:
            return [
                "category",
                "directoryInfo",
                "pointElement",
                "verticalPenetration",
                "zone",
                "lineElement",
                "areaElement",
                "opening",
                "unit",
                "level",
                "facility",
            ]
        elif ontology == cls.FACILITY_2:
            defined_collection_order = [
                "facility",
                "level",
                "unit",
                "category",
                "directoryInfo",
                "pointElement",
                "verticalPenetration",
                "zone",
                "lineElement",
                "structure",
                "areaElement",
                "opening"
            ]
            defined_collection_order_lower = [c.lower().strip() for c in defined_collection_order]
            other_collections = [c for c in collectionNames if c.lower().strip() not in defined_collection_order_lower]
            return defined_collection_order + other_collections
        elif ontology == cls.CUSTOM:
            pre_defined_collection_order = [
                "level",
                "facility",
            ]
            defined_collection_order = [c for c in pre_defined_collection_order if c.lower().strip() in collectionNames_lower] # Only include if collectionName is in collections
            defined_collection_order_lower = [c.lower().strip() for c in defined_collection_order]
            other_collections = [c for c in collectionNames if c.lower().strip() not in defined_collection_order_lower]
            return defined_collection_order + other_collections
        else: # Including NoOntology
            return []
