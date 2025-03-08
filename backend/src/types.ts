export interface Route {
    id: number;
    name: string;
    sport: string;
    distance: number;
    komoot_id?: number;
    gpx_file_path?: string;
    route_points?: [number, number, number][];
    min_lat?: number;
    min_lng?: number;
    max_lat?: number;
    max_lng?: number;
}

export interface RouteFilters {
    sport?: string;
    collections?: string;
    minDistance?: number;
    maxDistance?: number;
    minBounds?: string;
    maxBounds?: string;
    limit?: number;
}
