import json

from database import engine
from fastapi import APIRouter, FastAPI, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models.komoot_route import KomootRoute, KomootRoutePublic
from sqlmodel import Session, SQLModel, select
from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosed

SQLModel.metadata.create_all(bind=engine)

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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


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


@app.get("/komoot-route/{id}", response_model=KomootRoutePublic)
def get_komoot_route(id: int):
    with Session(engine) as session:
        route = KomootRoute.get_by_id(session, id)
    return route


@app.get("/komoot-routes", response_model=list[KomootRoutePublic])
def get_komoot_routes(limit: int = 1000):
    with Session(engine) as session:
        routes = KomootRoute.get_all(session, limit)
    return routes


@app.get("/test")
def test():
    json_data = '{"id": 1990783694, "name": "test", "sport": "racebike", "routePoints": {"lat": 1, "lng": 2, "elevation": 3}}'
    # json_data = '[["aa", "bb", "cc"]]'
    print(KomootRoutePublic.model_validate_json(json_data))


@app.get("/update-gpx")
def update_gpx():
    with Session(engine) as session:
        komoot_routes = KomootRoute.get_all(session, limit=None)
        for komoot_route in komoot_routes:
            if komoot_route.potential_route_update:
                komoot_route.add_gpx_file(session)
                # break

        return "done"
