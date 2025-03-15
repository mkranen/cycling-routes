import enum
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional, TypeAlias, Union

from dotenv import load_dotenv
from humps import camelize
from komPYoot import API, TourOwner, TourStatus, TourType
from pydantic import computed_field, validator
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import JSON, Column, Field, Relationship, Session, SQLModel, select
from utils.route import LAT, LNG, get_min_max, get_track_points

logger = logging.getLogger(__name__)

# Constants section
DOWNLOAD_DIR: str = "./downloads"
DEFAULT_SOURCES: list[str] = ["personal", "gravelritten", "gijs_bruinsma"]

# Type aliases for better type safety
KomootUserId: TypeAlias = str
SportType: TypeAlias = Literal[
    "race_bike", "mountain_bike", "gravel_bike", "touring_bike", "hike", "run"
]

komoot_sport_to_slug = {
    "racebike": "race_bike",
    "mtb": "mountain_bike",
    "mtb_easy": "gravel_bike",
    "touringbicycle": "touring_bike",
    "hike": "hike",
    "run": "run",
}

gpx_file_path = "./downloads"


def to_camel(string):
    return camelize(string)


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string to UTC datetime object"""
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc)


def ensure_download_dir(source: str) -> Path:
    """Ensure download directory exists and return Path object"""
    source_dir = Path(DOWNLOAD_DIR) / source
    source_dir.mkdir(parents=True, exist_ok=True)
    return source_dir


class KomootConfig(SQLModel):
    user_id: KomootUserId
    tour_type: TourType
    tour_status: TourStatus | None
    tour_owner: TourOwner | None = None

    @classmethod
    def get_source_configs(cls, api: API) -> dict[str, "KomootConfig"]:
        return {
            "personal": cls(
                user_id=api.user_details["user_id"],
                tour_type=TourType.PLANNED,
                tour_owner=TourOwner.SELF,
                tour_status=None,
            ),
            "gravelritten": cls(
                user_id="751970492203",
                tour_type=TourType.PLANNED,
                tour_status=TourStatus.PUBLIC,
            ),
            "gijs_bruinsma": cls(
                user_id="753944379383",
                tour_type=TourType.PLANNED,
                tour_status=TourStatus.PUBLIC,
            ),
        }


class KomootError(Exception):
    """Base exception for Komoot-related errors"""

    pass


class KomootImportError(KomootError):
    """Raised when there's an error importing routes"""

    pass


class KomootDownloadError(KomootError):
    """Raised when there's an error downloading routes"""

    pass


class Point(SQLModel):
    lat: float
    lng: float
    elevation: float


class Sport(str, enum.Enum):
    race_bike = "race_bike"
    mountain_bike = "mountain_bike"
    gravel_bike = "gravel_bike"
    touring_bike = "touring_bike"
    hike = "hike"
    run = "run"


SportEnum: ENUM = ENUM(
    Sport,
    name="sport",
    create_constraint=True,
    create_type=False,
    metadata=SQLModel.metadata,
    validate_strings=True,
)


class SportPublic(SQLModel):
    id: int
    name: str
    slug: Optional[str] = None


class Collection(SQLModel, table=True):
    __tablename__ = "collections"

    id: int = Field(default=None, primary_key=True)
    name: str
    slug: Optional[str] = None

    routes: list["CollectionRoute"] = Relationship(back_populates="collection")

    class Config:
        populate_by_name = True
        alias_generator = to_camel

    def __repr__(self):
        return f"Collection(id={self.id}, name={self.name}, slug={self.slug})"


class CollectionRoute(SQLModel, table=True):
    __tablename__ = "collection_routes"

    id: int = Field(default=None, primary_key=True)
    collection_id: int = Field(default=None, foreign_key="collections.id")
    route_id: int = Field(default=None, foreign_key="routes.id")

    collection: Collection = Relationship(back_populates="routes")
    route: "Route" = Relationship(back_populates="collections")


class CollectionRoutePublic(SQLModel):
    id: int
    collection_id: int
    route_id: int


# Komoot


class KomootRoute(SQLModel, table=True):
    __tablename__ = "komoot_routes"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Unique identifier for the route"
    )
    type: str
    name: str = Field(..., min_length=1, description="Name of the route")
    source: dict = Field(sa_column=Column(JSON))
    routing_version: Optional[str] = None
    status: str
    date: datetime
    kcal_active: int
    kcal_resting: int
    distance: float
    duration: int
    elevation_up: float
    elevation_down: float
    sport: str
    query: str
    constitution: int
    changed_at: datetime
    potential_route_update: bool = Field(default=False)
    gpx_file_path: Optional[str] = None

    start_point: list["KomootStartPoint"] = Relationship(back_populates="route")
    path_points: list["KomootPathPoint"] = Relationship(back_populates="route")
    surface_summary: list["KomootSurfaceSummary"] = Relationship(back_populates="route")
    difficulty: list["KomootDifficulty"] = Relationship(back_populates="route")
    segments: list["KomootSegment"] = Relationship(back_populates="route")
    way_type_summary: list["KomootWayTypeSummary"] = Relationship(
        back_populates="route"
    )
    tour_information: list["KomootTourInformation"] = Relationship(
        back_populates="route"
    )
    routes: list["Route"] = Relationship(back_populates="komoot")

    class Config:
        populate_by_name = True
        alias_generator = to_camel

    def __repr__(self):
        return f"KomootRoute(id={self.id}, name={self.name}, type={self.type})"

    @staticmethod
    def get_by_id(session: Session, id: int):
        return session.exec(select(KomootRoute).where(KomootRoute.id == id)).first()

    @staticmethod
    def get_all(session: Session, limit: Optional[int] = 100):
        if limit is None:
            return session.exec(select(KomootRoute)).all()

        return session.exec(select(KomootRoute).limit(limit)).all()

    @staticmethod
    def import_from_json(
        session: Session, route_data: Dict, collection_slug: str | None = None
    ) -> "KomootRoute":
        try:
            # Check if route already exists
            komoot_route = session.exec(
                select(KomootRoute).where(KomootRoute.id == route_data["id"])
            ).first()

            if not komoot_route:
                komoot_route = KomootRoute(
                    id=route_data["id"],
                    type=route_data["type"],
                    name=route_data["name"],
                    source=route_data["source"],
                    routing_version=route_data.get("routing_version", None),
                    status=route_data["status"],
                    date=parse_datetime(route_data["date"]),
                    kcal_active=route_data["kcal_active"],
                    kcal_resting=route_data["kcal_resting"],
                    distance=route_data["distance"],
                    duration=route_data["duration"],
                    elevation_up=route_data["elevation_up"],
                    elevation_down=route_data["elevation_down"],
                    sport=route_data["sport"],
                    query=route_data["query"],
                    constitution=route_data["constitution"],
                    changed_at=parse_datetime(route_data["changed_at"]),
                    potential_route_update=route_data["potential_route_update"],
                )
                session.add(komoot_route)

            # Add start point
            if not komoot_route.start_point:
                start_point = KomootStartPoint(
                    route_id=komoot_route.id,
                    lat=route_data["start_point"]["lat"],
                    lng=route_data["start_point"]["lng"],
                    alt=route_data["start_point"]["alt"],
                )
                session.add(start_point)

            # Add difficulty
            if "difficulty" in route_data and not komoot_route.difficulty:
                difficulty = KomootDifficulty(
                    route_id=komoot_route.id,
                    grade=route_data["difficulty"]["grade"],
                    explanation_technical=route_data["difficulty"][
                        "explanation_technical"
                    ],
                    explanation_fitness=route_data["difficulty"]["explanation_fitness"],
                )
                session.add(difficulty)

            # Add tour information
            if not komoot_route.tour_information:
                for tour_info in route_data.get("tour_information", []):
                    tour = KomootTourInformation(
                        route_id=komoot_route.id,
                        type=tour_info["type"],
                        segments=tour_info["segments"],
                    )
                    session.add(tour)

            # Add path points
            if not komoot_route.path_points:
                for point in route_data.get("path", []):
                    path_point = KomootPathPoint(
                        route_id=komoot_route.id,
                        lat=point["location"]["lat"],
                        lng=point["location"]["lng"],
                        index=point["index"],
                        end_index=point.get("end_index"),
                        reference=point.get("reference"),
                        segment_type=point.get("segment_type"),
                    )
                    session.add(path_point)

            # Add segments
            if not komoot_route.segments:
                for segment in route_data.get("segments", []):
                    seg = KomootSegment(
                        route_id=komoot_route.id,
                        type=segment["type"],
                        from_index=segment["from"],
                        to_index=segment["to"],
                    )
                    session.add(seg)

            # Add summaries
            if not komoot_route.surface_summary:
                for surface in route_data.get("summary", {}).get("surfaces", []):
                    surface_summary = KomootSurfaceSummary(
                        route_id=komoot_route.id,
                        type=surface["type"],
                        amount=surface["amount"],
                    )
                    session.add(surface_summary)

            if not komoot_route.way_type_summary:
                for way_type in route_data.get("summary", {}).get("way_types", []):
                    way_type_summary = KomootWayTypeSummary(
                        route_id=komoot_route.id,
                        type=way_type["type"],
                        amount=way_type["amount"],
                    )
                    session.add(way_type_summary)

            # Create or update Route
            route = (
                session.exec(
                    select(Route).where(Route.komoot_id == komoot_route.id)
                ).first()
                or Route()
            )

            route.name = route.name or komoot_route.name
            route.komoot_id = route.komoot_id or komoot_route.id
            route.distance = route.distance or komoot_route.distance
            route.gpx_file_path = route.gpx_file_path or komoot_route.gpx_file_path

            if not route.sport and komoot_route.sport in komoot_sport_to_slug:
                route.sport = Sport(komoot_sport_to_slug[komoot_route.sport])

            session.add(route)

            if collection_slug:
                collection = session.exec(
                    select(Collection).where(Collection.slug == collection_slug)
                ).first()
                if collection:
                    existing_route = session.exec(
                        select(CollectionRoute).where(
                            CollectionRoute.collection_id == collection.id,
                            CollectionRoute.route_id == route.id,
                        )
                    ).first()

                    if not existing_route:
                        collection_route = CollectionRoute(
                            route_id=route.id,
                            collection_id=collection.id,
                        )
                        session.add(collection_route)

            session.commit()
            return komoot_route

        except Exception as e:
            session.rollback()
            logger.error(
                f"Error importing route {route_data.get('name', 'Unknown')}: {str(e)}"
            )
            raise

    @classmethod
    def import_from_file(
        cls, session: Session, file_path: str, collection_slug: str
    ) -> List["KomootRoute"]:
        with open(file_path, "r") as f:
            routes_data = json.load(f)

        imported_routes = []
        for route_data in routes_data:
            try:
                route = cls.import_from_json(session, route_data, collection_slug)
                imported_routes.append(route)
                logger.info(f"Imported {route.name}")
            except Exception as e:
                logger.error(f"Skipping route due to error: {str(e)}")
                continue

        return imported_routes

    @classmethod
    def download_from_api(
        cls, sources: list[str] = DEFAULT_SOURCES, download_dir: str = DOWNLOAD_DIR
    ) -> dict[str, list]:
        """
        Download routes from Komoot API and save to JSON files.

        Args:
            sources: List of source identifiers to download from
            download_dir: Directory to save downloaded files

        Returns:
            dict: Dictionary mapping source names to their downloaded routes data

        Raises:
            KomootDownloadError: If there's an error during download
            ValueError: If invalid source provided
        """
        try:
            load_dotenv()
            email_id = os.getenv("KOMOOT_EMAIL")
            password = os.getenv("KOMOOT_PASSWORD")

            if not email_id or not password:
                raise KomootDownloadError("Missing Komoot credentials")

            api = API()
            api.login(email_id, password)

            source_configs = {
                "personal": {
                    "user_id": api.user_details["user_id"],
                    "tour_type": TourType.PLANNED,
                    "tour_owner": TourOwner.SELF,
                    "tour_status": None,
                },
                "gravelritten": {
                    "user_id": "751970492203",
                    "tour_type": TourType.PLANNED,
                    "tour_status": TourStatus.PUBLIC,
                },
                "gijs_bruinsma": {
                    "user_id": "753944379383",
                    "tour_type": TourType.PLANNED,
                    "tour_status": TourStatus.PUBLIC,
                },
            }

            downloaded_routes = {}

            for source in sources:
                if source not in source_configs:
                    logger.error(f"Skipping unknown source: {source}")
                    continue

                config = source_configs[source]
                source_dir = f"{download_dir}/{source}"
                Path(source_dir).mkdir(parents=True, exist_ok=True)

                # Get tours list
                if source == "personal":
                    tours = api.get_user_tours_list(
                        tour_type=config["tour_type"],
                        tour_owner=config["tour_owner"],
                        tour_status=config["tour_status"],
                    )
                else:
                    tours = api.get_tours_list(
                        user_id=config["user_id"],
                        tour_type=config["tour_type"],
                        tour_status=config["tour_status"],
                    )

                downloaded_routes[source] = tours

                # Save tours JSON
                json_path = f"{source_dir}/{source}_routes.json"
                with open(json_path, "w") as f:
                    json.dump(tours, f, indent=4)

                # Download GPX files
                for index, tour in enumerate(tours):
                    file_name = api.download_tour_gpx_file(tour, download_dir)
                    logger.info(
                        f"Downloaded {source} - {index + 1}/{len(tours)}: {file_name}"
                    )

                logger.info(f"Downloaded {len(tours)} tours from {source}")

            return downloaded_routes

        except Exception as e:
            logger.error(f"Error downloading routes: {str(e)}")
            raise KomootDownloadError(str(e))

    @classmethod
    def download_and_import(
        cls,
        session: Session,
        sources: list[str] = ["personal", "gravelritten", "gijs_bruinsma"],
    ) -> None:
        """Download routes from API and import them to database."""
        downloaded_routes = cls.download_from_api(sources)

        for source, routes_data in downloaded_routes.items():
            cls.bulk_import(session, routes_data, collection_slug=source)

    @classmethod
    def bulk_import(
        cls,
        session: Session,
        routes_data: list[Dict],
        collection_slug: str | None = None,
    ) -> list["KomootRoute"]:
        """Import multiple routes in a single transaction"""
        imported = []
        try:
            for route_data in routes_data:
                route = cls.import_from_json(session, route_data, collection_slug)
                imported.append(route)
                logger.info(f"Imported {route.name}")
            session.commit()
            logger.info(f"Imported {len(imported)} routes")
            return imported
        except Exception as e:
            session.rollback()
            raise KomootImportError(f"Bulk import failed: {str(e)}")


class KomootRoutePublic(SQLModel):
    id: int
    name: str
    sport: str = None
    type: Optional[str] = None
    distance: Optional[float] = None
    elevation_up: Optional[float] = None
    changed_at: Optional[datetime] = None
    gpx_file_path: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class KomootRoutePublicWithRoutePoints(SQLModel):
    id: int
    name: str
    sport: str = None
    type: Optional[str] = None
    distance: Optional[float] = None
    elevation_up: Optional[float] = None
    changed_at: Optional[datetime] = None
    gpx_file_path: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class KomootStartPoint(SQLModel, table=True):
    __tablename__ = "komoot_start_points"

    id: int = Field(default=None, primary_key=True)
    lat: float = Field(default=None)
    lng: float = Field(default=None)
    alt: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="start_point")


class KomootPathPoint(SQLModel, table=True):
    __tablename__ = "komoot_path_points"

    id: int = Field(default=None, primary_key=True)
    lat: float = Field(default=None)
    lng: float = Field(default=None)
    index: int = Field(default=None)
    end_index: int = Field(default=None, nullable=True)
    reference: str = Field(default=None, nullable=True)
    segment_type: str = Field(default=None, nullable=True)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="path_points")


class KomootSurfaceSummary(SQLModel, table=True):
    __tablename__ = "komoot_surface_summaries"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    amount: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="surface_summary")


class KomootDifficulty(SQLModel, table=True):
    __tablename__ = "komoot_difficulties"

    id: int = Field(default=None, primary_key=True)
    grade: str = Field(default=None)
    explanation_technical: str = Field(default=None)
    explanation_fitness: str = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="difficulty")


class KomootSegment(SQLModel, table=True):
    __tablename__ = "komoot_segments"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    from_index: int = Field(default=None)
    to_index: int = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="segments")


class KomootWayTypeSummary(SQLModel, table=True):
    __tablename__ = "komoot_way_type_summaries"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    amount: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="way_type_summary")


class KomootTourInformation(SQLModel, table=True):
    __tablename__ = "komoot_tour_information"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    segments: dict = Field(sa_column=Column(JSON))

    route_id: int | None = Field(default=None, foreign_key="komoot_routes.id")
    route: KomootRoute | None = Relationship(back_populates="tour_information")


# Route


class Route(SQLModel, table=True):
    __tablename__ = "routes"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1)
    sport: Sport = Field(sa_column=Column(ENUM(Sport)))
    distance: Optional[float] = Field(None, ge=0)
    komoot_id: Optional[int] = Field(default=None, foreign_key="komoot_routes.id")
    gpx_file_path: Optional[str] = None
    route_points: Optional[List[List[float]]] = Field(
        sa_column=Column(JSON), default=[]
    )
    min_lat: Optional[float] = None
    min_lng: Optional[float] = None
    max_lat: Optional[float] = None
    max_lng: Optional[float] = None

    komoot: KomootRoute | None = Relationship(back_populates="routes")
    collections: list["CollectionRoute"] = Relationship(
        back_populates="route", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @staticmethod
    def get_by_id(session: Session, id: int):
        return session.exec(select(Route).where(Route.id == id)).first()

    @staticmethod
    def get_by_komoot_id(session: Session, komoot_id: int):
        return session.exec(select(Route).where(Route.komoot_id == komoot_id)).first()

    @staticmethod
    def get_all(
        session: Session,
        sport: Optional[Sport] = None,
        collections: Optional[List[str]] = None,
        minDistance: Optional[float] = None,
        maxDistance: Optional[float] = None,
        minBounds: Optional[List[float]] = None,
        maxBounds: Optional[List[float]] = None,
        limit: Optional[int] = 100,
    ):
        query = select(Route)

        if minDistance is not None:
            query = query.where(Route.distance >= minDistance)

        if maxDistance is not None:
            query = query.where(Route.distance <= maxDistance)

        if minBounds is not None:
            query = query.where(Route.max_lat >= minBounds[0])
            query = query.where(Route.max_lng >= minBounds[1])

        if maxBounds is not None:
            query = query.where(Route.min_lat <= maxBounds[0])
            query = query.where(Route.min_lng <= maxBounds[1])

        if sport is not None:
            query = query.where(Route.sport == sport)

        if collections is not None:
            query = (
                query.join(CollectionRoute)
                .join(Collection)
                .filter(Collection.slug.in_(collections))
            )

        if limit is not None:
            query = query.limit(limit)

        return session.exec(query).all()

    def add_gpx_file(self, session: Session):
        if not self.name:
            return

        file_name = self.name.replace("/", "-") + ".gpx"
        self.gpx_file_path = file_name
        session.add(self)
        session.commit()

    def add_route_points(self, session: Session):
        if not self.gpx_file_path or not self.sport:
            return

        collection_slug = self.collections[0].collection.slug
        activity_type = self.sport
        file_path = (
            f"{gpx_file_path}/{collection_slug}/{activity_type}/{self.gpx_file_path}"
        )

        file = Path(file_path)
        if not file.exists():
            return

        file_string = file.read_text()
        route_points = get_track_points(file_string)
        self.route_points = route_points
        self.min_lat, self.max_lat = get_min_max(self.route_points, LAT)
        self.min_lng, self.max_lng = get_min_max(self.route_points, LNG)

        session.add(self)
        session.commit()

    def populate_bounding_box(self, session: Session):
        if not self.route_points:
            return

        self.min_lat, self.max_lat = get_min_max(self.route_points, LAT)
        self.min_lng, self.max_lng = get_min_max(self.route_points, LNG)

        session.add(self)
        session.commit()

    def update_from_komoot(self, komoot_route: KomootRoute) -> None:
        """Update route data from Komoot route"""
        self.name = komoot_route.name
        self.distance = komoot_route.distance
        self.komoot_id = komoot_route.id
        if komoot_route.sport in komoot_sport_to_slug:
            self.sport = Sport(komoot_sport_to_slug[komoot_route.sport])


class RoutePublic(SQLModel):
    id: int
    name: str
    sport: Optional[Sport] = None
    distance: Optional[float] = None
    collections: Optional[List[CollectionRoutePublic]] = None
    route_points: Optional[List[List[float]]] = Field(
        None, description="List of [lat, lng] coordinates"
    )

    @validator("route_points")
    def validate_route_points(
        cls, v: Optional[List[List[float]]]
    ) -> Optional[List[List[float]]]:
        if v is not None:
            for point in v:
                if len(point) != 2:
                    raise ValueError("Each point must be [lat, lng]")
                if not (-90 <= point[0] <= 90):
                    raise ValueError("Invalid latitude")
                if not (-180 <= point[1] <= 180):
                    raise ValueError("Invalid longitude")
        return v

    @computed_field(description="source")
    @property
    def source(self) -> str:
        return "Komoot" if self.komoot else "Strava"

    komoot: KomootRoutePublic | None = None

    class Config:
        populate_by_name = True
        alias_generator = to_camel
