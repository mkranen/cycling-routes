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
        "line-color": ["case", ["boolean", ["feature-state", "hover"], false], "#f00", "#00b"],
        "line-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 1, 0.5],
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
        "line-opacity": 1,
        "line-width": 6,
    },
};
