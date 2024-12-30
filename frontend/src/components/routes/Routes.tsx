import { Layer, Source } from "@vis.gl/react-maplibre";
import { LineLayerSpecification } from "maplibre-gl";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { Route } from "../../types/route";
import { useGetRoutesQuery } from "../app/apiSlice";
import { setInteractiveLayerIds } from "../map/mapSlice";

export default function Routes() {
    const [routes, setRoutes] = useState<JSX.Element[]>([]);
    const { data: routesData } = useGetRoutesQuery({ limit: 100 });
    const dispatch = useDispatch();

    async function loadRoutes(routeData: Route[]) {
        const allRoutes: JSX.Element[] = [];

        for (const route of routeData) {
            const routePoints = await loadTrackPoints(route);
            if (routePoints) {
                allRoutes.push(routePoints);
            }
        }

        const interactiveLayerIds: string[] = [];
        for (const route of allRoutes) {
            const layerId = route.props?.children?.props?.id;
            interactiveLayerIds.push(layerId);
        }
        dispatch(setInteractiveLayerIds(interactiveLayerIds));

        setRoutes(allRoutes);
    }

    async function loadTrackPoints(route): Promise<JSX.Element | null> {
        if (!route.routePoints) {
            return null;
        }

        const routePoints = route.routePoints.map((point) => [point.lng, point.lat]);
        const routeSource = {
            id: `route-source-${route.id}`,
            type: "FeatureCollection",
            features: [
                {
                    type: "Feature",
                    geometry: {
                        type: "LineString",
                        coordinates: routePoints,
                    },
                },
            ],
        };

        const routeLayer: LineLayerSpecification = {
            id: `route-layer-${route.id}`,
            type: "line",
            source: `route-source-${route.id}`,
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": "#00b",
                "line-opacity": 0.4,
                "line-width": 5,
            },
        };

        return (
            <Source key={route.id} id={`route-source-${route.id}`} type="geojson" data={routeSource}>
                <Layer {...routeLayer} />
            </Source>
        );
    }

    useEffect(() => {
        if (routesData) {
            loadRoutes(routesData);
        }
    }, [routesData]);

    return routes;
}
