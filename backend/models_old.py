from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    name = Column(String)
    source = Column(JSON)
    routing_version = Column(String)
    status = Column(String)
    date = Column(DateTime)
    kcal_active = Column(Integer)
    kcal_resting = Column(Integer)
    distance = Column(Float)
    duration = Column(Integer)
    elevation_up = Column(Float)
    elevation_down = Column(Float)
    sport = Column(String)
    query = Column(String)
    constitution = Column(Integer)
    changed_at = Column(DateTime)
    potential_route_update = Column(Boolean, default=False)

    # Relationships
    start_point = relationship("StartPoint", uselist=False, back_populates="route")
    difficulty = relationship("Difficulty", uselist=False, back_populates="route")
    tour_information = relationship("TourInformation", back_populates="route")
    path_points = relationship("PathPoint", back_populates="route")
    segments = relationship("Segment", back_populates="route")
    surface_summary = relationship("SurfaceSummary", back_populates="route")
    way_type_summary = relationship("WayTypeSummary", back_populates="route")


class StartPoint(Base):
    __tablename__ = "start_points"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    lat = Column(Float)
    lng = Column(Float)
    alt = Column(Float)

    route = relationship("Route", back_populates="start_point")


class Difficulty(Base):
    __tablename__ = "difficulties"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    grade = Column(String)
    explanation_technical = Column(String)
    explanation_fitness = Column(String)

    route = relationship("Route", back_populates="difficulty")


class TourInformation(Base):
    __tablename__ = "tour_information"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    segments = Column(JSON)  # Store segments as JSON array

    route = relationship("Route", back_populates="tour_information")


class PathPoint(Base):
    __tablename__ = "path_points"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    lat = Column(Float)
    lng = Column(Float)
    index = Column(Integer)
    end_index = Column(Integer, nullable=True)
    reference = Column(String, nullable=True)
    segment_type = Column(String, nullable=True)

    route = relationship("Route", back_populates="path_points")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    from_index = Column(Integer)
    to_index = Column(Integer)

    route = relationship("Route", back_populates="segments")


class SurfaceSummary(Base):
    __tablename__ = "surface_summaries"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    amount = Column(Float)

    route = relationship("Route", back_populates="surface_summary")


class WayTypeSummary(Base):
    __tablename__ = "way_type_summaries"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    amount = Column(Float)

    route = relationship("Route", back_populates="way_type_summary")


# Base.metadata.drop_all(
#     engine,
#     tables=[
#         Base.metadata.tables["route"],
#         Base.metadata.tables["start_point"],
#         Base.metadata.tables["difficulty"],
#         Base.metadata.tables["tour_information"],
#         Base.metadata.tables["path_point"],
#         Base.metadata.tables["segment"],
#         Base.metadata.tables["surface_summary"],
#         Base.metadata.tables["way_type_summary"],
#     ],
# )

# Base.metadata.create_all(engine)
