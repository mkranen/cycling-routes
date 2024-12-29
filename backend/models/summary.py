from database import Base
from sqlalchemy.orm import relationship
from sqlmodel import Column, Float, ForeignKey, Integer, String


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


class Difficulty(Base):
    __tablename__ = "difficulties"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    grade = Column(String)
    explanation_technical = Column(String)
    explanation_fitness = Column(String)

    route = relationship("Route", back_populates="difficulty")
