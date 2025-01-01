import enum
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from humps import camelize
from sqlmodel import JSON, Column, Enum, Field, Relationship, Session, SQLModel, select
from utils.gpx import get_track_points

komoot_sport_to_slug = {
    "racebike": "race_bike",
    "mtb": "mountain_bike",
    "mtb_easy": "gravel_bike",
    "touringbicycle": "touring_bike",
    "hike": "hike",
    "run": "run",
}


def to_camel(string):
    return camelize(string)


# Supporting models


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


SportType: Enum = Enum(
    Sport,
    name="post_status_type",
    create_constraint=True,
    metadata=SQLModel.metadata,
    validate_strings=True,
)


class SportPublic(SQLModel):
    id: int
    name: str
    slug: Optional[str] = None


# Komoot


class KomootRoute(SQLModel, table=True):
    __tablename__ = "komoot_routes"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    name: str
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
    routes: list["Route"] = Relationship(back_populates="komoot_route")

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

    def update_route(self, session: Session):
        route = Route.get_by_komoot_id(session, self.id)
        if route is None:
            route = Route()

        if not route.name:
            route.name = self.name
        if not route.komoot_id:
            route.komoot_id = self.id
        if not route.gpx_file_path:
            route.gpx_file_path = self.gpx_file_path

        if not route.sport and self.sport in komoot_sport_to_slug:
            route.sport = Sport(komoot_sport_to_slug[self.sport])

        session.add(route)
        session.commit()


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
    name: str
    sport: Sport = Field(sa_column=Column(Enum(Sport)))
    komoot_id: Optional[int] = Field(default=None, foreign_key="komoot_routes.id")
    gpx_file_path: Optional[str] = None
    route_points: Optional[List[List[float]]] = Field(
        sa_column=Column(JSON), default=[]
    )

    komoot_route: KomootRoute | None = Relationship(back_populates="routes")
    # sport: Sport | None = Relationship(back_populates="routes")

    @staticmethod
    def get_by_komoot_id(session: Session, komoot_id: int):
        return session.exec(select(Route).where(Route.komoot_id == komoot_id)).first()

    @staticmethod
    def get_all(
        session: Session, sport: Optional[Sport] = None, limit: Optional[int] = 100
    ):
        query = select(Route)

        if limit is not None:
            query = query.limit(limit)

        if sport is not None:
            query = query.where(Route.sport == sport)

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

        activity_type = self.sport.slug
        file_path = f"./gpx_files/{activity_type}/{self.gpx_file_path}"

        file = Path(file_path)
        if not file.exists():
            return

        file_string = file.read_text()
        route_points = get_track_points(file_string)
        self.route_points = route_points
        session.add(self)
        session.commit()


class RoutePublic(SQLModel):
    id: int
    name: str
    sport: Optional[Sport] = None
    route_points: Optional[List[List[float]]]

    komoot_route: KomootRoutePublic | None = None

    class Config:
        populate_by_name = True
        alias_generator = to_camel
