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
import { collections, setSelectedRoute } from "../routes/routeSlice.ts";
import { setBounds, setLatitude, setLongitude } from "./mapSlice";

function Map() {
    // Collection color mapping
    const collectionColors = useMemo(
        () => ({
            personal: fullConfig.theme.colors.cyan["700"], // Cyan for personal routes
            gravelritten: fullConfig.theme.colors.green["600"], // Green for gravelritten routes
            gijs_bruinsma: fullConfig.theme.colors.yellow["500"], // Orange for gijs_bruinsma routes
            default: fullConfig.theme.colors.gray["500"], // Gray for any other collection
        }),
        []
    );

    // Map legend component
    const MapLegend = () => {
        return (
            <div className="absolute z-10 p-2 bg-white rounded shadow-md bottom-4 right-4">
                <div className="mb-1 text-sm font-bold">Collections</div>
                {collections.map((collection) => (
                    <div key={collection.value} className="flex items-center gap-2 mb-1">
                        <div
                            className="w-4 h-4 rounded-full"
                            style={{
                                backgroundColor:
                                    collectionColors[collection.value as keyof typeof collectionColors] ||
                                    collectionColors.default,
                            }}
                        />
                        <span className="text-xs">{collection.label}</span>
                    </div>
                ))}
            </div>
        );
    };

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
    const selectedCollections = useSelector((state: RootState) => state.route.selectedCollections);
    const minDistance = useSelector((state: RootState) => state.route.minDistance);
    const maxDistance = useSelector((state: RootState) => state.route.maxDistance);
    const mapBounds = useSelector((state: RootState) => state.map.bounds);
    const { data: routesData } = useGetRoutesQuery({
        limit,
        sport,
        collections: selectedCollections?.map((collection) => collection.value),
        minDistance,
        maxDistance,
        mapBounds,
    });
    const dispatch = useDispatch();
    const geolocateControlRef = useRef<any>(null);

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
                // Use a match expression to set color based on collection property
                "line-color": [
                    "match",
                    ["get", "collection"],
                    "personal",
                    collectionColors.personal,
                    "gravelritten",
                    collectionColors.gravelritten,
                    "gijs_bruinsma",
                    collectionColors.gijs_bruinsma,
                    collectionColors.default,
                ],
                "line-opacity": 0.5,
                "line-width": 5,
            },
        };
    }, [collectionColors]);

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
            .map((route: RouteType) => {
                // Determine the collection this route belongs to
                let collectionName = "default";
                if (route.collections && route.collections.length > 0) {
                    // Try to find the collection information
                    const collectionId = route.collections[0].collection_id;
                    const collection = collections.find((c) => {
                        // Find the matching collection from our predefined list
                        // We need to match by ID, but we only have the slug in our definitions
                        return route.collections?.some((rc) => {
                            return rc.collection_id === collectionId && c.value === getCollectionSlug(rc.collection_id);
                        });
                    });
                    if (collection) {
                        collectionName = collection.value;
                    }
                }

                return {
                    id: route.id,
                    type: "Feature",
                    properties: {
                        collection: collectionName,
                    },
                    geometry: {
                        type: "LineString",
                        coordinates: route.routePoints.map((point) => [point[1], point[0]]),
                    },
                };
            });

        return {
            type: "FeatureCollection",
            features: routeFeatures,
        };
    }, [routesData]);

    // Helper function to get collection slug by id
    function getCollectionSlug(collectionId: number): string | undefined {
        // This is a temporary workaround - TODO:fetch this from the backend
        // For now, assume collection IDs 1, 2, 3 correspond to the three collections
        switch (collectionId) {
            case 1:
                return "personal";
            case 2:
                return "gravelritten";
            case 3:
                return "gijs_bruinsma";
            default:
                return undefined;
        }
    }

    // Helper function to get collection label by id
    function getCollectionLabel(collectionId: number): string {
        // Find the collection in our predefined list
        const collection = collections.find((c) => c.value === getCollectionSlug(collectionId));
        return collection ? collection.label : "Unknown";
    }

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

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (geolocateControlRef.current) {
                try {
                    geolocateControlRef.current.trigger();
                } catch (error) {
                    // Silently handle any errors
                }
            }
        }, 1000);

        return () => clearTimeout(timeoutId);
    }, []);

    // Get map style URL from environment variables
    const tomTomKey = (import.meta as any).env?.VITE_TOMTOM_KEY || "";
    const mapStyleUrl = `https://api.tomtom.com/style/2/custom/style/dG9tdG9tQEBANEFTRUE5QUt5TFBKdWRqbztiODVmNTFmYS00OTNlLTQ4ZjEtYjYwZC1mZmU0N2JlMjljODY=/drafts/0.json?key=${tomTomKey}`;

    return (
        <div className="relative w-full h-full">
            <MaplibreMap
                {...viewState}
                ref={mapRef}
                className="w-full h-full"
                interactiveLayerIds={["routes"]}
                // mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
                // mapStyle={`https://api.tomtom.com/style/2/custom/style/dG9tdG9tQEBANEFTRUE5QUt5TFBKdWRqbzs5NDg2NWRjYy1hZTgyLTRmMTYtYmNiNS05ZDQwOTY0OTZjMmU=.json?key=${import.meta.env.VITE_TOMTOM_KEY}`}
                mapStyle={mapStyleUrl}
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
                    ref={geolocateControlRef}
                    positionOptions={{
                        enableHighAccuracy: false,
                        timeout: 6000,
                        maximumAge: 0,
                    }}
                    auto={true}
                    onGeolocate={(event) => {
                        dispatch(setLongitude(event.coords.longitude));
                        dispatch(setLatitude(event.coords.latitude));
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
                        {popupData?.route?.collections && popupData.route.collections.length > 0 && (
                            <div className="text-sm opacity-75">
                                Collection: {getCollectionLabel(popupData.route.collections[0].collection_id)}
                            </div>
                        )}
                    </Popup>
                )}
            </MaplibreMap>

            {/* Map Legend */}
            <MapLegend />
        </div>
    );
}

export default Map;
