import {
    GeolocateControl,
    Layer,
    LineLayer,
    MapLayerMouseEvent,
    Map as MaplibreMap,
    MapRef,
    Popup,
    Source,
} from "@vis.gl/react-maplibre";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fullConfig } from "../../App";
import { RootState } from "../../app/store.ts";
import type { RouteCollection, RoutePopupData, ViewState } from "../../types/map";
import { RouteType } from "../../types/route.ts";
import { useGetRoutesQuery } from "../app/apiSlice.ts";
import { setSelectedRoute } from "../routes/routeSlice.ts";
import { setBounds, setLatitude, setLongitude } from "./mapSlice";

function Map() {
    const mapRef = useRef<MapRef>(null);
    const latitude = useSelector((state: RootState) => state.map.latitude);
    const longitude = useSelector((state: RootState) => state.map.longitude);
    const zoom = useSelector((state: RootState) => state.map.zoom);
    const selectedRoute = useSelector((state: RootState) => state.route.selectedRoute);
    const previousSelectedRoute = useSelector((state: RootState) => state.route.previousSelectedRoute);
    const [hoveredRouteId, setHoveredRouteId] = useState<number | null>(null);
    const [popupVisible, setPopupVisible] = useState(false);
    const [popupData, setPopupData] = useState<RoutePopupData | null>(null);
    const [viewState, setViewState] = useState<ViewState>({ longitude, latitude, zoom });
    const limit = useSelector((state: RootState) => state.route.limit);
    const sport = useSelector((state: RootState) => state.route.sport);
    const minDistance = useSelector((state: RootState) => state.route.minDistance);
    const maxDistance = useSelector((state: RootState) => state.route.maxDistance);
    const mapBounds = useSelector((state: RootState) => state.map.bounds);
    const { data: routesData } = useGetRoutesQuery({ limit, sport, minDistance, maxDistance, mapBounds });
    const dispatch = useDispatch();

    const routesLayer = useMemo((): LineLayer => {
        return {
            id: "routes",
            source: "",
            type: "line",
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": fullConfig.theme.colors.cyan["700"],
                "line-opacity": 0.5,
                "line-width": 5,
            },
        };
    }, [fullConfig]);

    const highlightedRoutesLayer = useMemo((): LineLayer => {
        return {
            id: "highlighted-route",
            source: "",
            type: "line",
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": fullConfig.theme.colors.cyan["800"],
                "line-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 1, 0],
                "line-width": 8,
            },
        };
    }, [fullConfig]);

    const selectedRoutesLayer = useMemo((): LineLayer => {
        return {
            id: "selected-route",
            source: "",
            type: "line",
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": fullConfig.theme.colors.cyan["900"],
                "line-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 1, 0],
                "line-width": 8,
            },
        };
    }, [fullConfig]);

    const selectedRoutesBackgroundLayer = useMemo((): LineLayer => {
        return {
            id: "selected-route-background",
            source: "",
            type: "line",
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": fullConfig.theme.colors.white,
                "line-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 1, 0],
                "line-width": 14,
            },
        };
    }, [fullConfig]);

    const routesFeaturesData = useMemo((): RouteCollection | null => {
        if (!routesData) return null;

        const routeFeatures = routesData
            .filter((route: RouteType) => route.routePoints)
            .map((route: RouteType) => ({
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

        return routesData?.find((route: RouteType) => route.id === routeId);
    }

    function selectRoute(event: MapLayerMouseEvent) {
        const route = getFirstRoute(event);
        if (!route) {
            dispatch(setSelectedRoute(null));
            return;
        }

        dispatch(setSelectedRoute(route));
    }

    function highlightRoute(event: MapLayerMouseEvent) {
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

    function updateBounds() {
        if (!mapRef.current) {
            return;
        }

        const bounds = mapRef.current.getBounds().toArray();
        dispatch(setBounds(bounds));
    }

    useEffect(() => {
        if (!mapRef.current) {
            return;
        }

        mapRef.current.setFeatureState({ source: "routes", id: hoveredRouteId }, { hover: true });
    }, [hoveredRouteId]);

    useEffect(() => {
        if (!mapRef.current || !selectedRoute) {
            return;
        }

        mapRef.current.setFeatureState({ source: "routes", id: selectedRoute.id }, { selected: true });
    }, [selectedRoute]);

    useEffect(() => {
        if (!mapRef.current || !previousSelectedRoute) {
            return;
        }

        mapRef.current.setFeatureState({ source: "routes", id: previousSelectedRoute.id }, { selected: false });
    }, [previousSelectedRoute]);

    return (
        <MaplibreMap
            {...viewState}
            ref={mapRef}
            className="w-full h-full"
            interactiveLayerIds={["routes"]}
            // mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
            // mapStyle={`https://api.tomtom.com/style/2/custom/style/dG9tdG9tQEBANEFTRUE5QUt5TFBKdWRqbzs5NDg2NWRjYy1hZTgyLTRmMTYtYmNiNS05ZDQwOTY0OTZjMmU=.json?key=${import.meta.env.VITE_TOMTOM_KEY}`}
            mapStyle={`https://api.tomtom.com/style/2/custom/style/dG9tdG9tQEBANEFTRUE5QUt5TFBKdWRqbztiODVmNTFmYS00OTNlLTQ4ZjEtYjYwZC1mZmU0N2JlMjljODY=/drafts/0.json?key=${
                import.meta.env.VITE_TOMTOM_KEY
            }`}
            onMove={(evt) => setViewState(evt.viewState)}
            onMoveEnd={() => updateBounds()}
            onClick={(event: MapLayerMouseEvent) => {
                selectRoute(event);
            }}
            onMouseEnter={(event: MapLayerMouseEvent) => {
                highlightRoute(event);
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
                    <Layer {...selectedRoutesLayer} source="routes" />
                    <Layer beforeId="selected-route" {...selectedRoutesBackgroundLayer} source="routes" />
                    <Layer beforeId="selected-route-background" {...highlightedRoutesLayer} source="routes" />
                    <Layer beforeId="highlighted-route" {...routesLayer} source="routes" />
                </Source>
            )}

            {popupVisible && (
                <Popup
                    longitude={popupData?.event.lngLat.lng}
                    latitude={popupData?.event.lngLat.lat}
                    closeButton={false}
                    closeOnClick={false}
                    offset={[0, -10]}
                    className="text-base-100 [&_.maplibregl-popup-content]:bg-slate-800 [&_.maplibregl-popup-content]:py-2 [&_.maplibregl-popup-content]:px-4 [&_.maplibregl-popup-content]:rounded [&_.maplibregl-popup-tip]:border-y-slate-800"
                >
                    <div className="text-base">{popupData?.route?.name}</div>
                </Popup>
            )}
        </MaplibreMap>
    );
}

export default Map;
