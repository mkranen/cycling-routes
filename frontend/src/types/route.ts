export type TrackPoint = {
    elevation?: number;
    time?: string;
};

export type TrackPoints = TrackPoint[] & {
    minLon?: number;
    maxLon?: number;
    minLat?: number;
    maxLat?: number;
};

export type RoutePoint = {
    lng: number;
    lat: number;
    elevation?: number;
    time?: string;
};

export type Route = {
    type: string;
    kcalResting: number;
    changedAt: string;
    id: number;
    distance: number;
    potentialRouteUpdate: boolean;
    name: string;
    duration: number;
    gpxFilePath: string | null;
    source: string;
    elevationUp: number;
    routingVersion: string | null;
    elevationDown: number;
    status: string;
    sport: "racebike" | "mtb_easy" | "touringbicycle" | "hike";
    date: string;
    query: string;
    kcalActive: number;
    constitution: number;
    routePoints: RoutePoint[];
};

export type Routes = Route[];
