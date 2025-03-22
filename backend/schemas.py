from typing import List, Tuple

from pydantic import BaseModel


class RouteSegment(BaseModel):
    id: int | None = None
    route_id: int
    start_point: List[float]
    end_point: List[float]
    geometry: Tuple[List[float], List[float]]
