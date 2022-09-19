from enum import Enum


class Ontology(Enum):
    FACILITY_1 = 'facility-1.0'
    FACILITY_2 = 'facility-2.0'
    UNKNOWN = 'unknown'

    @classmethod
    def _missing_(cls, name):
        if name == name.lower():
            return cls.UNKNOWN
        else:
            return cls(name.lower())
