import { GeolocateControl, Layer, MapLayerMouseEvent, Map as MaplibreMap, Popup, Source } from "@vis.gl/react-maplibre";
import React, { useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import { Route } from "../../types/route.ts";
import { useGetRoutesQuery } from "../app/apiSlice.ts";
import { setLatitude, setLongitude } from "./mapSlice";
import { routesLayer } from "./mapStyle.ts";

type RouteData = {
    route: Route;
    event: any;
};

function Map() {
    const latitude = useSelector((state: RootState) => state.map.latitude);
    const longitude = useSelector((state: RootState) => state.map.longitude);
    const zoom = useSelector((state: RootState) => state.map.zoom);
    const [popupVisible, setPopupVisible] = useState(false);
    const [popupData, setPopupData] = useState<RouteData | null>(null);
    const { data: routesData } = useGetRoutesQuery({ limit: 100 });
    const interactiveLayerIds = useSelector((state: RootState) => state.map.interactiveLayerIds);
    const dispatch = useDispatch();

    const [viewState, setViewState] = React.useState({
        longitude,
        latitude,
        zoom,
    });

    const routesFeaturesData = useMemo(() => {
        if (!routesData) return null;

        const routeFeatures = routesData
            .filter((route: Route) => route.routePoints)
            .map((route: Route) => ({
                type: "Feature",
                geometry: {
                    type: "LineString",
                    coordinates: route.routePoints.map((point) => [point.lng, point.lat]),
                },
            }));

        return {
            id: "routes",
            type: "FeatureCollection",
            features: routeFeatures,
        };
    }, [routesData]);

    function getFirstRoute(event: MapLayerMouseEvent) {
        const features = event.features;
        if (!features || features.length === 0) return null;

        const routeId = features[0].layer?.id.split("route-layer-")[1];
        if (!routeId) return null;

        return routesData?.find((route: Route) => route.id === Number(routeId));
    }

    function showRoutePopup(event: MapLayerMouseEvent) {
        const route = getFirstRoute(event);
        if (!route) {
            hideRoutePopup();
            return;
        }

        setPopupData({ route, event });
        setPopupVisible(true);
    }

    function hideRoutePopup() {
        setPopupVisible(false);
        setPopupData(null);
    }

    return (
        <MaplibreMap
            {...viewState}
            className="w-full h-full"
            interactiveLayerIds={interactiveLayerIds}
            mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
            onMove={(evt) => setViewState(evt.viewState)}
            onClick={(event: MapLayerMouseEvent) => {
                const route = getFirstRoute(event);
            }}
            onMouseEnter={(event: MapLayerMouseEvent) => {
                showRoutePopup(event);
            }}
            onMouseLeave={() => {
                hideRoutePopup();
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
                <Source type="geojson" data={routesFeaturesData}>
                    <Layer {...routesLayer} />
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
