from datetime import datetime
from typing import List, Optional

from humps import camelize
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import JSON, Column, Field, Relationship, Session, SQLModel, select
from utils.gpx import get_track_points


def to_camel(string):
    return camelize(string)


class Point(SQLModel):
    lat: float
    lng: float
    elevation: float


class Route(SQLModel, table=True):
    __tablename__ = "routes"

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
    route_points: Optional[List[Point]] = Field(sa_column=Column(JSON), default=[])
    # route_points: str

    start_point: list["StartPoint"] = Relationship(back_populates="route")
    path_points: list["PathPoint"] = Relationship(back_populates="route")
    surface_summary: list["SurfaceSummary"] = Relationship(back_populates="route")
    difficulty: list["Difficulty"] = Relationship(back_populates="route")
    segments: list["Segment"] = Relationship(back_populates="route")
    way_type_summary: list["WayTypeSummary"] = Relationship(back_populates="route")
    tour_information: list["TourInformation"] = Relationship(back_populates="route")

    class Config:
        populate_by_name = True
        alias_generator = to_camel

    def __repr__(self):
        return f"Route(id={self.id}, name={self.name}, type={self.type})"

    @staticmethod
    def get_by_id(session: Session, id: int):
        return session.exec(select(Route).where(Route.id == id)).first()

    @staticmethod
    def get_all(session: Session, limit: Optional[int]):
        if limit is None:
            return session.exec(select(Route)).all()

        return session.exec(select(Route).limit(limit)).all()

    def add_gpx_file(self, session: Session):
        file_name = self.name.replace("/", "-") + ".gpx"
        activity_type = self.sport
        file_path = f"./gpx_files/{activity_type}/{file_name}"

        with open(file_path, "r") as file:
            file_string = file.read()
            route_points = get_track_points(file_string)
            self.route_points = route_points
            self.gpx_file_path = file_name
            session.add(self)
            session.commit()


class RoutePublic(SQLModel):
    id: int
    name: str
    sport: str = None
    type: Optional[str] = None
    distance: Optional[float] = None
    elevation_up: Optional[float] = None
    changed_at: Optional[datetime] = None
    gpx_file_path: Optional[str] = None
    route_points: Optional[List[Point]] = Field(sa_column=Column(JSON))
    # route_points: Optional[str] = None

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class StartPoint(SQLModel, table=True):
    __tablename__ = "start_points"

    id: int = Field(default=None, primary_key=True)
    lat: float = Field(default=None)
    lng: float = Field(default=None)
    alt: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="start_point")


class PathPoint(SQLModel, table=True):
    __tablename__ = "path_points"

    id: int = Field(default=None, primary_key=True)
    lat: float = Field(default=None)
    lng: float = Field(default=None)
    index: int = Field(default=None)
    end_index: int = Field(default=None, nullable=True)
    reference: str = Field(default=None, nullable=True)
    segment_type: str = Field(default=None, nullable=True)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="path_points")


class SurfaceSummary(SQLModel, table=True):
    __tablename__ = "surface_summaries"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    amount: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="surface_summary")


class Difficulty(SQLModel, table=True):
    __tablename__ = "difficulties"

    id: int = Field(default=None, primary_key=True)
    grade: str = Field(default=None)
    explanation_technical: str = Field(default=None)
    explanation_fitness: str = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="difficulty")


class Segment(SQLModel, table=True):
    __tablename__ = "segments"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    from_index: int = Field(default=None)
    to_index: int = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="segments")


class WayTypeSummary(SQLModel, table=True):
    __tablename__ = "way_type_summaries"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    amount: float = Field(default=None)

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="way_type_summary")


class TourInformation(SQLModel, table=True):
    __tablename__ = "tour_information"

    id: int = Field(default=None, primary_key=True)
    type: str = Field(default=None)
    segments: dict = Field(sa_column=Column(JSON))

    route_id: int | None = Field(default=None, foreign_key="routes.id")
    route: Route | None = Relationship(back_populates="tour_information")
