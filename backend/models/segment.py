from database import Base
from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    from_index = Column(Integer)
    to_index = Column(Integer)

    route = relationship("Route", back_populates="segments")


class TourInformation(Base):
    __tablename__ = "tour_information"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    type = Column(String)
    segments = Column(JSON)  # Store segments as JSON array

    route = relationship("Route", back_populates="tour_information")
