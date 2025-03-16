import json
import logging
import os
from pathlib import Path

# Configure logging
from logging_config import configure_logging

logger = configure_logging()

# Import configuration
from config import DEFAULT_SOURCES, DOWNLOAD_DIR, ROOT_DIR
from database import engine
from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from komoot import API, TourStatus, TourType
from models.models import (
    KomootRoute,
    KomootRoutePublic,
    KomootRoutePublicWithRoutePoints,
    Route,
    RoutePublic,
)
from sqlmodel import Session
from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosed

app = FastAPI()
router = APIRouter()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def get_session():
    with Session(engine) as session:
        yield session


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
