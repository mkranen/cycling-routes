from sqlalchemy import create_engine
from sqlalchemy.engine import URL

url = URL.create(
    drivername="postgresql",
    username="cycling-routes",
    host="localhost",
    database="cycling-routes",
    password="HYr5xe9j6cYANf",
)

engine = create_engine(url)
