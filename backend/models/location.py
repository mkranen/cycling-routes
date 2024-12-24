from database import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class StartPoint(Base):
    __tablename__ = "start_points"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    lat = Column(Float)
    lng = Column(Float)
    alt = Column(Float)

    route = relationship("Route", back_populates="start_point")


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
