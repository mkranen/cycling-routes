import type { LineLayer } from "@vis.gl/react-maplibre";

export const routesLayer: LineLayer = {
    id: "routes",
    source: "",
    // source: `route-source-${route.id}`,
    type: "line",
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

export const highlightedRoutesLayer: LineLayer = {
    id: "highlighted-routes",
    source: "",
    // source: `route-source-${route.id}`,
    type: "line",
    layout: {
        "line-join": "round",
        "line-cap": "round",
    },
    paint: {
        "line-color": "#00b",
        "line-opacity": 1,
        "line-width": 10,
    },
};
