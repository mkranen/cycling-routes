import type { LngLatLike, MapLayerMouseEvent } from "@vis.gl/react-maplibre";
import type { RouteType } from "./route";

// TODO: Replace with @vis.gl/react-maplibre ViewState
export interface ViewState {
    longitude: number;
    latitude: number;
    zoom?: number;
    pitch?: number;
    bearing?: number;
}

export interface RouteFeature {
    id: number;
    type: "Feature";
    geometry: {
        type: "LineString";
        coordinates: [number, number][];
    };
}

export interface RouteCollection {
    type: "FeatureCollection";
    features: RouteFeature[];
}

export interface RoutePopupData {
    route: RouteType;
    event: MapLayerMouseEvent;
    coordinates: LngLatLike;
}

export interface GeoJSONFeature {
    type: "Feature";
    geometry: {
        type: string;
        coordinates: number[];
    };
    properties?: Record<string, any>;
}

export interface GeoJSONCollection {
    type: "FeatureCollection";
    features: GeoJSONFeature[];
}
