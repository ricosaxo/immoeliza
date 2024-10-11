from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel

class Criteria(BaseModel):
    countries: str
    propertyTypes: str
    transactionTypes: str
    page: str
    trigger: str
    place: str
    client: str

class ProjectInfo(BaseModel):
    constructor: None
    groupId: int
    phase: None
    projectName: Optional[str]
    deliveryDate: None
    soldPercentage: Optional[int]
    unitsDisplayMode: None

class Cluster(BaseModel):
    minPrice: Optional[int]
    maxPrice: Optional[int]
    minRoom: None
    maxRoom: None
    minSurface: Optional[int]
    maxSurface: Optional[int]
    projectInfo: Optional[ProjectInfo]
    bedroomRange: str
    surfaceRange: str

class Flags(BaseModel):
    main: Optional[str]
    secondary: List[str]
    percentSold: Optional[int]

class Picture(BaseModel):
    smallUrl: Optional[str]
    mediumUrl: Optional[str]
    largeUrl: Optional[str]
    isVertical: bool

class Media(BaseModel):
    pictures: List[Picture]

class Location(BaseModel):
    country: str
    region: Optional[str]
    province: Optional[str]
    district: Optional[str]
    locality: str
    postalCode: str
    street: Optional[str]
    number: Optional[str]
    box: Optional[str]
    propertyName: Optional[str]
    floor: None
    latitude: Optional[float]
    longitude: Optional[float]
    distance: None
    approximated: None
    regionCode: Optional[str]
    type: None
    hasSeaView: None
    pointsOfInterest: None
    placeName: Optional[str]


class Property(BaseModel):
    type: str
    subtype: str
    title: Optional[str]
    bedroomCount: Optional[int]
    location: Location
    netHabitableSurface: Optional[int]
    landSurface: Optional[int]
    roomCount: Optional[int]


class Publication(BaseModel):
    publisherId: None
    visualisationOption: str
    size: str


class LifeAnnuity(BaseModel):
    lumpSum: int
    monthlyAmount: int
    estimatedPropertyValue: None
    isIndexed: None
    isJointAndSurvivorContract: None
    isBareOwnership: None
    contractMaximumDurationDescription: None
    annuitantCount: None
    annuitantAges: None


class PublicSale(BaseModel):
    status: str
    pendingOverbidAmount: None
    hasUniqueSession: None
    isForcedSale: None
    hasPendingOverbidRight: bool
    lastSessionReachedPrice: None
    date: None


class Sale(BaseModel):
    lifeAnnuity: Optional[LifeAnnuity]
    hasStartingPrice: Optional[bool]
    oldPrice: Optional[int]
    price: Optional[int]
    pricePerSqm: None
    publicSale: Optional[PublicSale]
    toBuild: None
    isSubjectToVat: None


class Transaction(BaseModel):
    certificateLogoUrl: Optional[str]
    certificate: Optional[str]
    type: str
    rental: None
    sale: Sale

class Price(BaseModel):
    type: str
    mainValue: Optional[int]
    alternativeValue: None
    additionalValue: Optional[int]
    oldValue: Optional[int]
    minRangeValue: Optional[int]
    maxRangeValue: Optional[int]
    mainDisplayPrice: str
    HTMLDisplayPrice: str
    alternativeDisplayPrice: str
    oldDisplayPrice: Optional[str]
    shortDisplayPrice: str
    accessibilityPrice: str
    label: str
    date: None
    language: str


class Result(BaseModel):
    id: int
    cluster: Cluster
    customerLogoUrl: Optional[str]
    customerName: str
    flags: Flags
    media: Media
    property: Property
    publication: Publication
    transaction: Transaction
    priceType: None
    price: Price
    isBookmarked: bool
    has360Tour: None
    hasVirtualTour: Optional[bool]
    advertisementId: None

class Location1(BaseModel):
    locality: str
    postalCode: str

class Property1(BaseModel):
    type: str
    subtype: str
    location: Location1

class Transaction1(BaseModel):
    type: str

class ResultsStorageItem(BaseModel):
    id: int
    property: Property1
    transaction: Transaction1


class Listing(BaseModel):
    property_id: int
    locality_name: str
    postal_code: str
    price: Optional[int] = None
    property_type: str
    property_subtype: str
    sale_type: str
    number_of_rooms: Optional[int] = None
    living_area_m2: Optional[int] = None

    @classmethod
    def from_result(cls, result: Result) -> Listing:
        return cls(
        property_id=result.id,
        locality_name=result.property.location.locality if result.property and result.property.location else None,
        postal_code=result.property.location.postalCode if result.property and result.property.location else None,
        price=result.price.mainValue if result.price else None,
        property_type=result.property.type if result.property else None,
        property_subtype=result.property.subtype if result.property else None,
        sale_type=result.transaction.type if result.transaction else None,
        number_of_rooms=result.property.bedroomCount if result.property else None,
        living_area_m2=result.property.netHabitableSurface if result.property else None,
    )

    