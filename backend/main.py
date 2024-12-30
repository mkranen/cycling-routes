import json

from database import engine
from fastapi import APIRouter, FastAPI, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models.route import Route, RoutePublic
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


@app.get("/routes", response_model=list[RoutePublic])
def get_routes():
    with Session(engine) as session:
        routes = session.exec(select(Route)).all()
    return routes


@app.get("/update-gpx")
def update_gpx():
    with Session(engine) as session:
        routes = Route.get_all(session)
        for route in routes:
            if route.potential_route_update:
                route.add_gpx_file(session)
                # break

        return "done"
