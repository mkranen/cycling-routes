from database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import Session, relationship


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
    gpx_file_path = Column(String, nullable=True)

    # Relationships
    start_point = relationship("StartPoint", uselist=False, back_populates="route")
    difficulty = relationship("Difficulty", uselist=False, back_populates="route")
    tour_information = relationship("TourInformation", back_populates="route")
    path_points = relationship("PathPoint", back_populates="route")
    segments = relationship("Segment", back_populates="route")
    surface_summary = relationship("SurfaceSummary", back_populates="route")
    way_type_summary = relationship("WayTypeSummary", back_populates="route")

    def __repr__(self):
        return f"Route(id={self.id}, name={self.name}, type={self.type})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }

    @staticmethod
    def get_all(db: Session):
        return db.query(Route).all()
