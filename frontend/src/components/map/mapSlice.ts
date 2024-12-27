import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "../../store";

interface MapState {
    longitude: number;
    latitude: number;
    zoom: number;
}

const initialState: MapState = {
    longitude: 5.13381188435385,
    latitude: 52.11015993159475,
    zoom: 15,
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
    },
});

export const { setLongitude, setLatitude, setZoom } = mapSlice.actions;
export const selectViewState = (state: RootState) => state.map;
export default mapSlice.reducer;
