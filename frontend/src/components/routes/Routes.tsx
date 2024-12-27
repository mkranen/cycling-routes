import { Layer, Source } from "@vis.gl/react-maplibre";
import React, { useEffect, useState } from "react";
import { getTrackPoints } from "./routes";

export default function Routes() {
    const [routes, setRoutes] = useState<JSX.Element[]>([]);

    async function loadAllRoutes() {
        const allRoutes: JSX.Element[] = [];
        const activityTypes = ["racebike", "roadbike", "mtb"];
        const fileNames = [
            "4 Utrechtse bergies.gpx",
            // "04-12 Waver.gpx",
            // "Wielrenroute - Zuid-Limburg - Amstel Gold Race-Lus 1.gpx",
        ];

        for (let i = 0; i < activityTypes.length; i++) {
            const activityType = activityTypes[i];
            const fileName = fileNames[i];
            const routePoints: JSX.Element = await loadTrackPoints({ activityType, fileName });
            allRoutes.push(routePoints);
        }
        setRoutes(allRoutes);
    }

    async function loadTrackPoints({
        activityType,
        fileName,
    }: {
        activityType: string;
        fileName: string;
    }): Promise<JSX.Element> {
        const fileDir = import.meta.env.VITE_GPX_DIR;
        const filePath = `${activityType}/${fileName}`;
        const normalizedFilePath = `${activityType}/${fileName}`
            .replace(/\.gpx$/, "")
            .replace(/\s+/g, "_")
            .toLowerCase();
        const fullFilePath = `${fileDir}/${filePath}`;
        const routePoints = getTrackPoints(await fetch(fullFilePath).then((r) => r.text()));

        const routeSource = {
            type: "FeatureCollection",
            features: [
                {
                    type: "Feature",
                    geometry: { type: "LineString", coordinates: routePoints },
                },
            ],
        };

        const routeLayer = {
            id: `layer-${normalizedFilePath}`,
            type: "line",
            source: `source-${normalizedFilePath}`,
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
            <Source key={normalizedFilePath} id={`source-${normalizedFilePath}`} type="geojson" data={routeSource}>
                <Layer {...routeLayer} />
            </Source>
        );
    }

    useEffect(() => {
        loadAllRoutes();
    }, []);

    return routes;
}
