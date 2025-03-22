import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import numpy as np

# Configure logging
from logging_config import configure_logging
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

logger = configure_logging()

# Import configuration
from config import DEFAULT_SOURCES, DOWNLOAD_DIR, ROOT_DIR
from database import engine
from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from komoot import API, TourStatus, TourType
from models.models import (
    Collection,
    CollectionRoute,
    KomootRoute,
    KomootRoutePublic,
    KomootRoutePublicWithRoutePoints,
    Route,
    RoutePublic,
    RouteSegment,
    Sport,
)
from schemas import RouteSegment as RouteSegmentSchema
from sqlmodel import Session
from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosed


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()
router = APIRouter()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods="*",
    allow_headers="*",
)


def find_intersections(line1: LineString, line2: LineString) -> List[Point]:
    """Find intersection points between two LineStrings."""
    try:
        intersection = line1.intersection(line2)
        if intersection.is_empty:
            return []
        if intersection.geom_type == "Point":
            # Check if the point is valid
            if not (np.isnan(intersection.x) or np.isnan(intersection.y)):
                return [intersection]
            return []
        # For MultiPoint, filter out invalid points
        valid_points = []
        for point in intersection.geoms:
            if not (np.isnan(point.x) or np.isnan(point.y)):
                valid_points.append(point)
        return valid_points
    except:
        return []


def create_segments_from_intersections(
    line: LineString, intersections: List[Point], route_id: int, start_segment_id: int
) -> List[RouteSegment]:
    """Create segments from a line and its intersection points."""
    if not intersections:
        return []

    # Create a buffer around the line
    line_buffer = line.buffer(0.0001)  # approximately 10 meters at the equator

    # Filter and sort intersection points
    valid_points = []
    for point in intersections:
        if not isinstance(point, Point):
            try:
                point = Point(point)
            except:
                continue
        # Only include points that are within the buffer
        if line_buffer.contains(point) and not (np.isnan(point.x) or np.isnan(point.y)):
            valid_points.append(point)

    if len(valid_points) < 2:
        return []

    # Sort points by their x coordinate (simple sorting)
    valid_points.sort(key=lambda p: p.x)

    segments = []
    current_id = start_segment_id

    # Create segments between consecutive points
    for i in range(len(valid_points) - 1):
        start_point = valid_points[i]
        end_point = valid_points[i + 1]

        # Create a new LineString between these points
        segment_line = LineString([start_point, end_point])

        if segment_line.geom_type == "LineString":
            # Convert NumPy arrays to Python lists
            coords = segment_line.coords.xy
            geometry = [coords[0].tolist(), coords[1].tolist()]

            segments.append(
                RouteSegment(
                    id=current_id,
                    route_id=route_id,
                    start_point=[float(start_point.x), float(start_point.y)],
                    end_point=[float(end_point.x), float(end_point.y)],
                    geometry=geometry,
                )
            )
            current_id += 1

    return segments


@app.get("/segments", response_model=List[RouteSegment])
def get_route_segments(
    db: Session = Depends(get_session),
    sport: Optional[str] = None,
    collections: Optional[List[str]] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    bounds: Optional[List[float]] = None,
):
    """
    Calculate segments from route intersections.
    Returns a list of segments where each segment represents a portion of a route between intersections.
    """
    # Build query based on filters
    query = db.query(Route.id, Route.route_points)

    if sport:
        query = query.filter(Route.sport == sport)
    if collections:
        query = query.join(CollectionRoute).filter(
            CollectionRoute.collection_id.in_(collections)
        )
    if min_distance:
        query = query.filter(Route.distance >= min_distance)
    if max_distance:
        query = query.filter(Route.distance <= max_distance)

    # Get all routes
    routes = query.all()

    # Convert routes to LineStrings
    route_lines = []
    for route in routes:
        if route.route_points:
            points = [(point[1], point[0]) for point in route.route_points]
            route_lines.append((route.id, LineString(points)))

    # Find all intersections and create segments
    all_segments = []
    segment_id = 0

    for i, (route1_id, line1) in enumerate(route_lines):
        for route2_id, line2 in route_lines[i + 1 :]:
            # Find intersections between the two routes
            intersections = find_intersections(line1, line2)

            if intersections:
                # Create segments for both routes
                segments1 = create_segments_from_intersections(
                    line1, intersections, route1_id, segment_id
                )
                segments2 = create_segments_from_intersections(
                    line2, intersections, route2_id, segment_id + len(segments1)
                )

                all_segments.extend(segments1)
                all_segments.extend(segments2)
                segment_id += len(segments1) + len(segments2)

    return all_segments


@app.post("/populate-segments")
def populate_route_segments(
    db: Session = Depends(get_session),
    sport: Optional[str] = None,
    collections: Optional[List[str]] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    bounds: Optional[List[float]] = None,
):
    """
    Calculate and store route segments in the database.
    Uses the same filtering options as the get_route_segments endpoint.
    """
    # Get segments using the existing function
    segments = get_route_segments(
        db=db,
        sport=sport,
        collections=collections,
        min_distance=min_distance,
        max_distance=max_distance,
        bounds=bounds,
    )

    # Store segments in the database
    stored_segments = []
    for segment in segments:
        db_segment = RouteSegment(
            route_id=segment.route_id,
            start_point=segment.start_point,
            end_point=segment.end_point,
            geometry=segment.geometry,
        )
        db.add(db_segment)
        stored_segments.append(db_segment)

    # Commit all segments
    db.commit()

    return {
        "message": f"Successfully stored {len(stored_segments)} segments",
        "segments": stored_segments,
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/ws")
def http_endpoint():
    return []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(json.dumps(data))
    except (WebSocketDisconnect, ConnectionClosed):
        manager.disconnect(websocket)


@router.get("/")
def home():
    return "response"


@app.get("/route/{id}", response_model=RoutePublic)
def get_route(*, session: Session = Depends(get_session), id: int):
    route = Route.get_by_id(session, id)

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route


@app.get("/routes", response_model=list[RoutePublic])
def get_routes(
    *,
    session: Session = Depends(get_session),
    sport: str = None,
    collections: str = None,
    min_distance: float = None,
    max_distance: float = None,
    min_bounds: str = None,
    max_bounds: str = None,
    limit: int = 1000,
):
    min_distance = min_distance * 1000 if min_distance else None
    max_distance = max_distance * 1000 if max_distance else None

    min_bounds_list = (
        list(reversed([float(i) for i in min_bounds.split(",")]))
        if min_bounds
        else None
    )
    max_bounds_list = (
        list(reversed([float(i) for i in max_bounds.split(",")]))
        if max_bounds
        else None
    )

    collections_list = collections.split(",") if collections else None

    routes = Route.get_all(
        session,
        sport,
        collections_list,
        min_distance,
        max_distance,
        min_bounds_list,
        max_bounds_list,
        limit,
    )
    return routes


@app.get("/komoot-route/{id}", response_model=KomootRoutePublicWithRoutePoints)
def get_komoot_route(*, session: Session = Depends(get_session), id: int):
    route = KomootRoute.get_by_id(session, id)

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route


@app.get("/komoot-routes", response_model=list[KomootRoutePublicWithRoutePoints])
def get_komoot_routes(*, session: Session = Depends(get_session), limit: int = 1000):
    routes = KomootRoute.get_all(session, limit)
    return routes


@app.get("/import-komoot-routes")
def import_komoot_routes(
    *,
    session: Session = Depends(get_session),
    sources: str = None,
):
    """
    Import routes from Komoot API and save them to the database.
    This endpoint uses the API directly to download and process routes.

    Args:
        sources: Comma-separated list of sources to import from
    """
    try:
        # Parse sources
        source_list = sources.split(",") if sources else DEFAULT_SOURCES

        # Use the download_and_import method
        KomootRoute.download_and_import(session, source_list)

        return {
            "status": "success",
            "message": f"Successfully imported routes from {', '.join(source_list)}",
        }
    except Exception as e:
        logger.error(f"Error importing routes: {str(e)}")
        return {"status": "error", "message": f"Error importing routes: {str(e)}"}


@app.get("/update-gpx")
def update_gpx(
    *,
    session: Session = Depends(get_session),
):
    routes = Route.get_all(session, limit=None)
    for route in routes:
        route.add_gpx_file(session)
        route.add_route_points(session)

    return "done"


# @app.get("/update-komoot-routes")
# def update_komoot_routes(
#     *,
#     session: Session = Depends(get_session),
# ):
#     komoot_routes = KomootRoute.get_all(session, limit=None)
#     for komoot_route in komoot_routes:
#         komoot_route.update_route(session)
#     return "done"


@app.get("/test")
def test():
    json_data = '{"id": 1990783694, "name": "test", "sport": "racebike", "routePoints": {"lat": 1, "lng": 2, "elevation": 3}}'
    # json_data = '[["aa", "bb", "cc"]]'
    print(KomootRoutePublic.model_validate_json(json_data))


@app.get("/import-and-save-komoot-routes")
def import_and_save_komoot_routes(
    *,
    session: Session = Depends(get_session),
    sources: str = None,
):
    """
    Import routes from Komoot API and save them to the database.

    Args:
        sources: Comma-separated list of sources to import from
    """
    # Parse sources
    source_list = sources.split(",") if sources else DEFAULT_SOURCES

    # Import routes
    try:
        KomootRoute.download_and_import(session, source_list)
        return {
            "status": "success",
            "message": f"Successfully imported routes from {', '.join(source_list)}",
        }
    except Exception as e:
        logger.error(f"Error importing routes: {str(e)}")
        return {"status": "error", "message": f"Error importing routes: {str(e)}"}
