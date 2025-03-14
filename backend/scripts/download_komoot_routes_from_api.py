#!/usr/bin/env python3

import json
import os

from dotenv import load_dotenv
from komPYoot import API, Sport, TourOwner, TourStatus, TourType

load_dotenv()

_DOWNLOAD_DIR = "./downloads"


def main(sources: list[str] = ["personal", "gravelritten", "gijs_bruinsma"]):
    email_id = os.getenv("KOMOOT_EMAIL")
    password = os.getenv("KOMOOT_PASSWORD")

    a = API()
    a.login(email_id, password)

    all_tours = []  # Create list to store all tours

    if "personal" in sources:
        personal_tours_file_name = "personal_routes.json"
        personal_tours = a.get_user_tours_list(
            tour_type=TourType.PLANNED,
            tour_owner=TourOwner.SELF,
        )
        all_tours.extend(personal_tours)

        personal_dir = _DOWNLOAD_DIR + "/personal"
        with open(personal_dir + "/" + personal_tours_file_name, "w") as f:
            json.dump(personal_tours, f, indent=4)

        for index, tour in enumerate(personal_tours):
            file_name = a.download_tour_gpx_file(tour, _DOWNLOAD_DIR)
            print(f"{index + 1}/{len(personal_tours)}: {file_name}")

    if "gravelritten" in sources:
        gravelritten_user_id = "751970492203"
        gravelritten_tours = a.get_tours_list(
            user_id=gravelritten_user_id,
            tour_type=TourType.PLANNED,
            tour_status=TourStatus.PUBLIC,
        )
        all_tours.extend(gravelritten_tours)

        gravelritten_dir = _DOWNLOAD_DIR + "/gravelritten"
        with open(gravelritten_dir + "/gravelritten_routes.json", "w") as f:
            json.dump(gravelritten_tours, f, indent=4)

        for index, tour in enumerate(gravelritten_tours):
            file_name = a.download_tour_gpx_file(tour, gravelritten_dir)
            print(f"{index + 1}/{len(gravelritten_tours)}: {file_name}")

    if "gijs_bruinsma" in sources:
        gijs_bruinsma_user_id = "753944379383"
        gijs_bruinsma_tours = a.get_tours_list(
            user_id=gijs_bruinsma_user_id,
            tour_type=TourType.PLANNED,
            tour_status=TourStatus.PUBLIC,
        )
        all_tours.extend(gijs_bruinsma_tours)

        gijs_bruinsma_dir = _DOWNLOAD_DIR + "/gijs_bruinsma"
        with open(gijs_bruinsma_dir + "/gijs_bruinsma_routes.json", "w") as f:
            json.dump(gijs_bruinsma_tours, f, indent=4)

        for index, tour in enumerate(gijs_bruinsma_tours):
            file_name = a.download_tour_gpx_file(tour, gijs_bruinsma_dir)
            print(f"{index + 1}/{len(gijs_bruinsma_tours)}: {file_name}")

    return all_tours


if __name__ == "__main__":
    import sys

    # Example usage: python download_komoot_routes_from_api.py personal gravelritten gijs_bruinsma
    sources = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else ["personal", "gravelritten", "gijs_bruinsma"]
    )

    tours = main(sources=sources)
