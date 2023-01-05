"""
Facility-2.0 Ontology Model
"""

class Facility_2:
    class COLLECTIONS:
        UNIT = "unit"
        STR = "structure"
        ZONE = "zone"
        LVL = "level"
        FCL = "facility"
        VRT = "verticalPenetration"
        OPN = "opening"
        DIR = "directoryInfo"
        PEL = "pointElement"
        LEL = "lineElement"
        AEL = "areaElement"
        CTG = "category"

    class BASE_ATTR:
        externalId = "externalId"
        originalId = "originalId"

    class UNIT(BASE_ATTR):
        categoryId = "categoryId"
        isOpenArea = "isOpenArea"
        isRoutable = "isRoutable"
        levelId = "levelId"
        occupants = "occupants"
        addressId = "addressId"
        addressRoomNumber = "addressRoomNumber"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class STR(BASE_ATTR):
        categoryId = "categoryId"
        levelId = "levelId"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class ZONE(BASE_ATTR):
        categoryId = "categoryId"
        setId = "setId"
        levelId = "levelId"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class LVL(BASE_ATTR):
        facilityId = "facilityId"
        ordinal = "ordinal"
        abbreviatedName = "abbreviatedName"
        heightAboveFacilityAnchor = "heightAboveFacilityAnchor"
        verticalExtent = "verticalExtent"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class FCL(BASE_ATTR):
        categoryId = "categoryId"
        occupants = "occupants"
        addressId = "addressId"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"
        anchorHeightAboveSeaLevel = "anchorHeightAboveSeaLevel"
        defaultLevelVerticalExtent = "defaultLevelVerticalExtent"

    class VRT(BASE_ATTR):
        setId = "setId"
        levelId = "levelId"
        categoryId = "categoryId"
        direction = "direction"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class OPN(BASE_ATTR):
        categoryId = "categoryId"
        levelId = "levelId"
        anchorPoint = "anchorPoint"

    class DIR(BASE_ATTR):
        streetAddress = "streetAddress"
        unit = "unit"
        locality = "locality"
        adminDivisions = "adminDivisions"
        postalCode = "postalCode"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        phoneNumber = "phoneNumber"
        website = "website"
        hoursOfOperation = "hoursOfOperation"

    class PEL(BASE_ATTR):
        categoryId = "categoryId"
        unitId = "unitId"
        isObstruction = "isObstruction"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"

    class LEL(BASE_ATTR):
        categoryId = "categoryId"
        unitId = "unitId"
        isObstruction = "isObstruction"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"
        obstructionArea = "obstructionArea"

    class AEL(BASE_ATTR):
        categoryId = "categoryId"
        unitId = "unitId"
        isObstruction = "isObstruction"
        obstructionArea = "obstructionArea"
        name = "name"
        nameSubtitle = "nameSubtitle"
        nameAlt = "nameAlt"
        anchorPoint = "anchorPoint"

    class CTG(BASE_ATTR):
        name = "name"