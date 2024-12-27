import { Layer, Source } from "@vis.gl/react-maplibre";
import React, { useEffect, useState } from "react";
import { getTrackPoints } from "./routes";
import { routeData } from "./routeSlice";

export default function Routes() {
    const [routes, setRoutes] = useState<JSX.Element[]>([]);

    async function loadAllRoutes() {
        const allRoutes: JSX.Element[] = [];

        for (const route of routeData) {
            const routePoints = await loadTrackPoints(route);
            allRoutes.push(routePoints);
        }

        setRoutes(allRoutes);
    }

    async function loadTrackPoints(route): Promise<JSX.Element> {
        const gpxDir = import.meta.env.VITE_GPX_DIR;
        const filePath = `${route.sport}/${route.gpxFilePath}`;
        const fullFilePath = `${gpxDir}/${filePath}`;
        const routePoints = getTrackPoints(await fetch(fullFilePath).then((r) => r.text()));

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
        loadAllRoutes();
    }, []);

    return routes;
}
