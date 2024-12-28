import { Position } from "geojson";

type PositionData = Position & { elevation: number };

export function getTrackPoints(fileString: string): PositionData[] {
    const parser = new DOMParser();
    const parsed = parser.parseFromString(fileString, "text/xml");
    const trackPoints: HTMLCollectionOf<Element> = parsed.getElementsByTagName("trkpt");
    const points: PositionData[] = [];

    for (const trackPoint of trackPoints) {
        const longitude = trackPoint.getAttribute("lon") || "0";
        const latitude = trackPoint.getAttribute("lat") || "0";
        const point = [parseFloat(longitude), parseFloat(latitude)] as PositionData;
        try {
            const elevation = trackPoint.getElementsByTagName("ele")[0]?.textContent || "0";
            point.elevation = parseFloat(elevation);
        } catch (e) {
            console.error(e);
        }
        points.push(point);
    }

    return points;
}
