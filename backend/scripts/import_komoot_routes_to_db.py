import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Dict, List

from database import engine
from models.models import (
    Collection,
    CollectionRoute,
    KomootDifficulty,
    KomootPathPoint,
    KomootRoute,
    KomootSegment,
    KomootStartPoint,
    KomootSurfaceSummary,
    KomootTourInformation,
    KomootWayTypeSummary,
    Route,
    Sport,
    komoot_sport_to_slug,
)
from sqlalchemy.orm import sessionmaker


def parse_datetime(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))


def import_route_data(
    route_data: Dict, collection_slug: str | None = None
) -> KomootRoute:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        # Check if route already exists
        komoot_route = (
            db.query(KomootRoute).filter(KomootRoute.id == route_data["id"]).first()
        )
        # if route:
        #     print(
        #         f"Route {route_data['name']} (ID: {route_data['id']}) already exists, skipping..."
        #     )
        if not komoot_route:
            # Create main route
            komoot_route = KomootRoute(
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

            db.add(komoot_route)

        # Check and create start point
        existing_start_point = (
            db.query(KomootStartPoint)
            .filter(KomootStartPoint.route_id == komoot_route.id)
            .first()
        )

        if not existing_start_point:
            start_point = KomootStartPoint(
                route_id=komoot_route.id,
                lat=route_data["start_point"]["lat"],
                lng=route_data["start_point"]["lng"],
                alt=route_data["start_point"]["alt"],
            )
            db.add(start_point)

        # Check and create difficulty
        if "difficulty" in route_data:
            existing_difficulty = (
                db.query(KomootDifficulty)
                .filter(KomootDifficulty.route_id == komoot_route.id)
                .first()
            )
            if not existing_difficulty:
                difficulty = KomootDifficulty(
                    route_id=komoot_route.id,
                    grade=route_data["difficulty"]["grade"],
                    explanation_technical=route_data["difficulty"][
                        "explanation_technical"
                    ],
                    explanation_fitness=route_data["difficulty"]["explanation_fitness"],
                )
                db.add(difficulty)

        # Check and create tour information
        existing_tour_info = (
            db.query(KomootTourInformation)
            .filter(KomootTourInformation.route_id == komoot_route.id)
            .all()
        )

        if not existing_tour_info:
            for tour_info in route_data.get("tour_information", []):
                tour = KomootTourInformation(
                    route_id=komoot_route.id,
                    type=tour_info["type"],
                    segments=tour_info["segments"],
                )
                db.add(tour)

        # Check and create path points
        existing_path_points = (
            db.query(KomootPathPoint)
            .filter(KomootPathPoint.route_id == komoot_route.id)
            .all()
        )

        if not existing_path_points:
            for point in route_data.get("path", []):
                path_point = KomootPathPoint(
                    route_id=komoot_route.id,
                    lat=point["location"]["lat"],
                    lng=point["location"]["lng"],
                    index=point["index"],
                    end_index=point.get("end_index"),
                    reference=point.get("reference"),
                    segment_type=point.get("segment_type"),
                )
                db.add(path_point)

        # Check and create segments
        existing_segments = (
            db.query(KomootSegment)
            .filter(KomootSegment.route_id == komoot_route.id)
            .all()
        )

        if not existing_segments:
            for segment in route_data.get("segments", []):
                seg = KomootSegment(
                    route_id=komoot_route.id,
                    type=segment["type"],
                    from_index=segment["from"],
                    to_index=segment["to"],
                )
                db.add(seg)

        # Check and create surface summaries
        existing_surfaces = (
            db.query(KomootSurfaceSummary)
            .filter(KomootSurfaceSummary.route_id == komoot_route.id)
            .all()
        )

        if not existing_surfaces:
            for surface in route_data.get("summary", {}).get("surfaces", []):
                surface_summary = KomootSurfaceSummary(
                    route_id=komoot_route.id,
                    type=surface["type"],
                    amount=surface["amount"],
                )
                db.add(surface_summary)

        # Check and create way type summaries
        existing_way_types = (
            db.query(KomootWayTypeSummary)
            .filter(KomootWayTypeSummary.route_id == komoot_route.id)
            .all()
        )

        if not existing_way_types:
            for way_type in route_data.get("summary", {}).get("way_types", []):
                way_type_summary = KomootWayTypeSummary(
                    route_id=komoot_route.id,
                    type=way_type["type"],
                    amount=way_type["amount"],
                )
                db.add(way_type_summary)

        # Update route
        route = db.query(Route).where(Route.komoot_id == komoot_route.id).first()

        if route is None:
            route = Route()

        if not route.name:
            route.name = komoot_route.name
        if not route.komoot_id:
            route.komoot_id = komoot_route.id
        if not route.distance:
            route.distance = komoot_route.distance
        if not route.gpx_file_path:
            route.gpx_file_path = komoot_route.gpx_file_path

        if not route.sport and komoot_route.sport in komoot_sport_to_slug:
            route.sport = Sport(komoot_sport_to_slug[komoot_route.sport])

        db.add(route)
        db.commit()

        # Check and create collection routes
        query = db.query(CollectionRoute)

        if collection_slug:
            collection = (
                db.query(Collection).filter(Collection.slug == collection_slug).first()
            )

        if collection:
            query = query.filter(CollectionRoute.collection_id == collection.id)
            existing_collection_routes = query.filter(
                CollectionRoute.route_id == route.id
            ).all()

            if len(existing_collection_routes) == 0:
                collection_route = CollectionRoute(
                    route_id=route.id,
                    collection_id=collection.id,
                )
                db.add(collection_route)

        db.commit()
        print(
            f"Successfully imported route: {komoot_route.name} (ID: {komoot_route.id})"
        )
        # return route

    except Exception as e:
        db.rollback()
        print(f"Error importing route {route_data.get('name', 'Unknown')}: {str(e)}")
        raise
    finally:
        db.close()


def import_routes_from_file(file_path: str, collection_slug: str) -> List[KomootRoute]:
    with open(file_path, "r") as f:
        routes_data = json.load(f)

    imported_routes = []
    for route_data in routes_data:
        try:
            route = import_route_data(route_data, collection_slug)
            imported_routes.append(route)
        except Exception as e:
            print(f"Skipping route due to error: {str(e)}")
            continue

    return imported_routes


if __name__ == "__main__":
    import sys

    # Example usage: python import_komoot_routes_to_db.py personal gravelritten gijs_bruinsma
    sources = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else ["personal", "gravelritten", "gijs_bruinsma"]
    )

    for source in sources:
        import_routes_from_file(f"downloads/{source}/{source}_routes.json", source)
