export interface Route {
    kcalActive: number;
    constitution: number;
    type: string;
    kcalResting: number;
    changedAt: string;
    id: number;
    distance: number;
    potentialRouteUpdate: boolean;
    name: string;
    duration: number;
    gpxFilePath: string;
    source: string;
    elevationUp: number;
    routingVersion: string | null;
    elevationDown: number;
    status: string;
    sport: string;
    date: string;
    query: string;
}
