import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { LngLatLike } from "maplibre-gl";

interface MapState {
    longitude: number;
    latitude: number;
    zoom: number;
    interactiveLayerIds: string[];
    bounds: LngLatLike | null;
}

const initialState: MapState = {
    longitude: 5.13381188435385,
    latitude: 52.11015993159475,
    zoom: 11,
    interactiveLayerIds: ["routes"],
    bounds: null,
};

export const mapSlice = createSlice({
    name: "map",
    initialState,
    reducers: {
        setLongitude: (state, action: PayloadAction<number>) => {
            state.longitude = action.payload;
        },
        setLatitude: (state, action: PayloadAction<number>) => {
            state.latitude = action.payload;
        },
        setZoom: (state, action: PayloadAction<number>) => {
            state.zoom = action.payload;
        },
        setInteractiveLayerIds: (state, action: PayloadAction<string[]>) => {
            state.interactiveLayerIds = action.payload;
        },
        setBounds: (state, action: PayloadAction<LngLatLike | null>) => {
            state.bounds = action.payload;
        },
    },
});

export const { setLongitude, setLatitude, setZoom, setInteractiveLayerIds, setBounds } = mapSlice.actions;
export default mapSlice.reducer;
