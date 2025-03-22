from typing import List, Optional, Tuple

from pydantic import BaseModel


class RouteSegment(BaseModel):
    id: int
    route_id: int
    start_point: List[float]
    end_point: List[float]
    geometry: Tuple[List[float], List[float]]

    class Config:
        from_attributes = True
