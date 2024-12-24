import json

from database import Base, engine, get_db
from fastapi import APIRouter, Depends, FastAPI, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Route
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosed

Base.metadata.create_all(bind=engine)

app = FastAPI()
router = APIRouter()

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


@app.get("/routes/")
def get_routes(db: Session = Depends(get_db)):
    # Use db session here
    routes = Route.get_all(db)
    return routes


app.include_router(router)
