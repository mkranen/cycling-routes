import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface MapState {
    longitude: number;
    latitude: number;
    zoom: number;
    interactiveLayerIds: string[];
}

const initialState: MapState = {
    longitude: 5.13381188435385,
    latitude: 52.11015993159475,
    zoom: 15,
    interactiveLayerIds: ["routes"],
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
    },
});

export const { setLongitude, setLatitude, setZoom, setInteractiveLayerIds } = mapSlice.actions;
export default mapSlice.reducer;
