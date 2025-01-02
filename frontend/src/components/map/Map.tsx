import {
    GeolocateControl,
    Layer,
    MapLayerMouseEvent,
    Map as MaplibreMap,
    MapRef,
    Popup,
    Source,
} from "@vis.gl/react-maplibre";
import React, { useMemo, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import type { RouteCollection, RoutePopupData, ViewState } from "../../types/map";
import { Route } from "../../types/route.ts";
import { useGetRoutesQuery } from "../app/apiSlice.ts";
import { setLatitude, setLongitude } from "./mapSlice";
import { routesLayer } from "./mapStyle.ts";

function Map() {
    const mapRef = useRef<MapRef>(null);
    const latitude = useSelector((state: RootState) => state.map.latitude);
    const longitude = useSelector((state: RootState) => state.map.longitude);
    const zoom = useSelector((state: RootState) => state.map.zoom);
    const interactiveLayerIds = useSelector((state: RootState) => state.map.interactiveLayerIds);
    const [hoveredRouteId, setHoveredRouteId] = useState<number | null>(null);
    const [popupVisible, setPopupVisible] = useState(false);
    const [popupData, setPopupData] = useState<RoutePopupData | null>(null);
    const [viewState, setViewState] = useState<ViewState>({ longitude, latitude, zoom });
    const limit = useSelector((state: RootState) => state.route.limit);
    const sport = useSelector((state: RootState) => state.route.sport);
    const minDistance = useSelector((state: RootState) => state.route.minDistance);
    const maxDistance = useSelector((state: RootState) => state.route.maxDistance);
    const { data: routesData } = useGetRoutesQuery({ limit, sport, minDistance, maxDistance });
    const dispatch = useDispatch();

    const routesFeaturesData = useMemo((): RouteCollection | null => {
        if (!routesData) return null;

        const routeFeatures = routesData
            .filter((route: Route) => route.routePoints)
            .map((route: Route) => ({
                id: route.id,
                type: "Feature",
                geometry: {
                    type: "LineString",
                    coordinates: route.routePoints.map((point) => [point[1], point[0]]),
                },
            }));

        return {
            type: "FeatureCollection",
            features: routeFeatures,
        };
    }, [routesData]);

    function getFirstRoute(event: MapLayerMouseEvent) {
        const features = event.features;
        if (!features || features.length === 0) return null;

        const routeId = features[0].id;
        if (!routeId) return null;

        return routesData?.find((route: Route) => route.id === routeId);
    }

    function showRoutePopup(event: MapLayerMouseEvent) {
        const route = getFirstRoute(event);
        if (!route) {
            hideRoutePopup();
            return;
        }

        setPopupData({ route, event, coordinates: event.lngLat });
        setPopupVisible(true);

        if (!mapRef.current) {
            return;
        }

        mapRef.current.setFeatureState({ source: "routes", id: hoveredRouteId }, { hover: false });
        mapRef.current.setFeatureState({ source: "routes", id: route.id }, { hover: true });
        setHoveredRouteId(route.id);
    }

    function hideRoutePopup() {
        setPopupVisible(false);
        setPopupData(null);

        if (!mapRef.current) {
            return;
        }

        mapRef.current.setFeatureState({ source: "routes", id: hoveredRouteId }, { hover: false });
        setHoveredRouteId(null);
    }

    return (
        <MaplibreMap
            {...viewState}
            ref={mapRef}
            className="w-full h-full"
            interactiveLayerIds={interactiveLayerIds}
            mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
            onMove={(evt) => setViewState(evt.viewState)}
            onClick={(event: MapLayerMouseEvent) => {
                const route = getFirstRoute(event);
            }}
            onMouseEnter={(event: MapLayerMouseEvent) => {
                showRoutePopup(event);
                if (mapRef.current) {
                    mapRef.current.getCanvas().style.cursor = "pointer";
                }
            }}
            onMouseLeave={() => {
                hideRoutePopup();
                if (mapRef.current) {
                    mapRef.current.getCanvas().style.cursor = "";
                }
            }}
        >
            <GeolocateControl
                positionOptions={{ enableHighAccuracy: true }}
                showAccuracyCircle={true}
                position="bottom-right"
                onGeolocate={(event) => {
                    dispatch(setLongitude(event.coords.longitude));
                    dispatch(setLatitude(event.coords.latitude));
                }}
                onError={(error) => {
                    console.log(error);
                }}
            />

            {routesFeaturesData && (
                <Source id="routes" type="geojson" data={routesFeaturesData}>
                    <Layer {...routesLayer} source="routes" />
                </Source>
            )}

            {popupVisible && (
                <Popup
                    longitude={popupData?.event.lngLat.lng}
                    latitude={popupData?.event.lngLat.lat}
                    closeButton={false}
                    closeOnClick={false}
                    offset={[0, -16]}
                    className="text-base-100 [&_.maplibregl-popup-content]:bg-blue-500 [&_.maplibregl-popup-content]:py-2 [&_.maplibregl-popup-content]:px-4 [&_.maplibregl-popup-tip]:border-y-blue-500"
                >
                    <div className="text-base">{popupData?.route?.name}</div>
                </Popup>
            )}
        </MaplibreMap>
    );
}

export default Map;
