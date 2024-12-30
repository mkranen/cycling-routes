import xml.etree.ElementTree as ET
from typing import List, Tuple


def get_track_points(file_string: str) -> List[Tuple[float, float, float]]:
    """
    Parse GPX file string and extract track points with elevation.

    Args:
        file_string: GPX file contents as string

    Returns:
        List of tuples containing (longitude, latitude, elevation)
    """
    root = ET.fromstring(file_string)
    track_points = root.findall(".//{*}trkpt")  # Use {*} for any namespace
    points = []

    for track_point in track_points:
        longitude = float(track_point.get("lon", "0"))
        latitude = float(track_point.get("lat", "0"))
        elevation = 0.0

        try:
            ele = track_point.find(".//{*}ele")
            if ele is not None and ele.text:
                elevation = float(ele.text)
        except Exception as e:
            print(f"Error parsing elevation: {e}")

        points.append({"lat": latitude, "lng": longitude, "elevation": elevation})

    return points
