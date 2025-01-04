import type { LineLayer } from "@vis.gl/react-maplibre";

export const routesLayer: LineLayer = {
    id: "routes",
    source: "",
    type: "line",
    layout: {
        "line-join": "round",
        "line-cap": "round",
    },
    paint: {
        "line-color": "#00b",
        "line-opacity": 0.5,
        "line-width": 5,
    },
};

export const highlightedRoutesLayer: LineLayer = {
    id: "highlighted-routes",
    source: "",
    type: "line",
    layout: {
        "line-join": "round",
        "line-cap": "round",
    },
    paint: {
        "line-color": "#f00",
        "line-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 1, 0],
        "line-width": 8,
    },
};
