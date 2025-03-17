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

export type CollectionRoute = {
    id: number;
    collection_id: number;
    route_id: number;
};

export type RouteType = {
    id?: number;
    name?: string;
    distance?: number;
    source?: string;
    // duration?: number;
    // elevationUp?: number;
    // elevationDown?: number;
    sport?: "racebike" | "mtb_easy" | "touringbicycle" | "hike";
    routePoints: RoutePoint[];
    komoot?: {
        id: string;
    };
    strava?: {
        id: string;
    };
    collections?: CollectionRoute[];
};
