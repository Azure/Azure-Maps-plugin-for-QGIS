from QGISPlugin.models.Ontology import Ontology


class Collection:
    @staticmethod
    def get_order(ontology):
        if ontology == Ontology.FACILITY_1:
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
        elif ontology == Ontology.FACILITY_2:
            return [
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
        elif ontology == Ontology.CUSTOM or ontology == Ontology.NOONTOLOGY:
            return [
                "facility",
                "level",
            ]
        else:
            return []
