import { Layer, Source } from "@vis.gl/react-maplibre";
import React, { useEffect, useState } from "react";
import { Route } from "../../types/route";
import { useGetRoutesQuery } from "../app/apiSlice";
import { getTrackPoints } from "./routes";

export default function Routes() {
    const [routes, setRoutes] = useState<JSX.Element[]>([]);
    const { data: routesData } = useGetRoutesQuery({});

    async function loadRoutes(routeData: Route[]) {
        const allRoutes: JSX.Element[] = [];

        for (const route of routeData) {
            const routePoints = await loadTrackPoints(route);
            if (routePoints) {
                allRoutes.push(routePoints);
            }
        }

        setRoutes(allRoutes);
    }

    async function loadTrackPoints(route): Promise<JSX.Element | null> {
        const gpxDir = import.meta.env.VITE_GPX_DIR;
        if (!route.gpxFilePath) {
            return null;
        }

        const filePath = `${route.sport}/${route.gpxFilePath}`;
        const fullFilePath = `${gpxDir}/${filePath}`;
        const routeData = await fetch(fullFilePath).then((r) => r.text());
        const routePoints = getTrackPoints(routeData);

        const routeSource = {
            id: `route-source-${route.id}`,
            type: "FeatureCollection",
            features: [
                {
                    type: "Feature",
                    geometry: { type: "LineString", coordinates: routePoints },
                },
            ],
        };

        const routeLayer = {
            id: `route-layer-${route.id}`,
            type: "line",
            source: `route-source-${route.id}`,
            layout: {
                "line-join": "round",
                "line-cap": "round",
            },
            paint: {
                "line-color": "#00b",
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
            loadRoutes(routesData.slice(0, 20));
        }
    }, [routesData]);

    return routes;
}
