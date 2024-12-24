import json
from datetime import datetime
from typing import Dict, List

from database import SessionLocal
from models import (
    Difficulty,
    PathPoint,
    Route,
    Segment,
    StartPoint,
    SurfaceSummary,
    TourInformation,
    WayTypeSummary,
)


def parse_datetime(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))


def import_route_data(route_data: Dict) -> Route:
    db = SessionLocal()
    try:
        # Check if route already exists
        existing_route = db.query(Route).filter(Route.id == route_data["id"]).first()
        if existing_route:
            print(
                f"Route {route_data['name']} (ID: {route_data['id']}) already exists, skipping..."
            )
            return existing_route

        # Create main route
        route = Route(
            id=route_data["id"],
            type=route_data["type"],
            name=route_data["name"],
            source=route_data["source"],
            routing_version=route_data.get("routing_version", None),
            status=route_data["status"],
            date=parse_datetime(route_data["date"]),
            kcal_active=route_data["kcal_active"],
            kcal_resting=route_data["kcal_resting"],
            distance=route_data["distance"],
            duration=route_data["duration"],
            elevation_up=route_data["elevation_up"],
            elevation_down=route_data["elevation_down"],
            sport=route_data["sport"],
            query=route_data["query"],
            constitution=route_data["constitution"],
            changed_at=parse_datetime(route_data["changed_at"]),
            potential_route_update=route_data["potential_route_update"],
        )

        db.add(route)

        # Check and create start point
        existing_start_point = (
            db.query(StartPoint).filter(StartPoint.route_id == route.id).first()
        )
        if not existing_start_point:
            start_point = StartPoint(
                route_id=route.id,
                lat=route_data["start_point"]["lat"],
                lng=route_data["start_point"]["lng"],
                alt=route_data["start_point"]["alt"],
            )
            db.add(start_point)

        # Check and create difficulty
        if "difficulty" in route_data:
            existing_difficulty = (
                db.query(Difficulty).filter(Difficulty.route_id == route.id).first()
            )
            if not existing_difficulty:
                difficulty = Difficulty(
                    route_id=route.id,
                    grade=route_data["difficulty"]["grade"],
                    explanation_technical=route_data["difficulty"][
                        "explanation_technical"
                    ],
                    explanation_fitness=route_data["difficulty"]["explanation_fitness"],
                )
                db.add(difficulty)

        # Check and create tour information
        existing_tour_info = (
            db.query(TourInformation).filter(TourInformation.route_id == route.id).all()
        )
        if not existing_tour_info:
            for tour_info in route_data.get("tour_information", []):
                tour = TourInformation(
                    route_id=route.id,
                    type=tour_info["type"],
                    segments=tour_info["segments"],
                )
                db.add(tour)

        # Check and create path points
        existing_path_points = (
            db.query(PathPoint).filter(PathPoint.route_id == route.id).all()
        )
        if not existing_path_points:
            for point in route_data.get("path", []):
                path_point = PathPoint(
                    route_id=route.id,
                    lat=point["location"]["lat"],
                    lng=point["location"]["lng"],
                    index=point["index"],
                    end_index=point.get("end_index"),
                    reference=point.get("reference"),
                    segment_type=point.get("segment_type"),
                )
                db.add(path_point)

        # Check and create segments
        existing_segments = db.query(Segment).filter(Segment.route_id == route.id).all()
        if not existing_segments:
            for segment in route_data.get("segments", []):
                seg = Segment(
                    route_id=route.id,
                    type=segment["type"],
                    from_index=segment["from"],
                    to_index=segment["to"],
                )
                db.add(seg)

        # Check and create surface summaries
        existing_surfaces = (
            db.query(SurfaceSummary).filter(SurfaceSummary.route_id == route.id).all()
        )
        if not existing_surfaces:
            for surface in route_data.get("summary", {}).get("surfaces", []):
                surface_summary = SurfaceSummary(
                    route_id=route.id,
                    type=surface["type"],
                    amount=surface["amount"],
                )
                db.add(surface_summary)

        # Check and create way type summaries
        existing_way_types = (
            db.query(WayTypeSummary).filter(WayTypeSummary.route_id == route.id).all()
        )
        if not existing_way_types:
            for way_type in route_data.get("summary", {}).get("way_types", []):
                way_type_summary = WayTypeSummary(
                    route_id=route.id,
                    type=way_type["type"],
                    amount=way_type["amount"],
                )
                db.add(way_type_summary)

        db.commit()
        print(f"Successfully imported route: {route.name} (ID: {route.id})")
        return route

    except Exception as e:
        db.rollback()
        print(f"Error importing route {route_data.get('name', 'Unknown')}: {str(e)}")
        raise
    finally:
        db.close()


def import_routes_from_file(file_path: str) -> List[Route]:
    with open(file_path, "r") as f:
        routes_data = json.load(f)

    imported_routes = []
    for route_data in routes_data:
        try:
            route = import_route_data(route_data)
            imported_routes.append(route)
        except Exception as e:
            print(f"Skipping route due to error: {str(e)}")
            continue

    return imported_routes


if __name__ == "__main__":
    import_routes_from_file("../routes/routes.json")
