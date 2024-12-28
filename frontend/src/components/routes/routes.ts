import { TrackPoint, TrackPoints } from "../../types/route";

export function getTrackPoints(fileString: string) {
    const parser = new DOMParser();
    const parsed = parser.parseFromString(fileString, "text/xml");
    const trackPoints: HTMLCollectionOf<Element> = parsed.getElementsByTagName("trkpt");
    const points: TrackPoints = [];

    for (const trackPoint of trackPoints) {
        const longitude = trackPoint.getAttribute("lon") || "0";
        const latitude = trackPoint.getAttribute("lat") || "0";
        const point = [parseFloat(longitude), parseFloat(latitude)] as TrackPoint;
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
