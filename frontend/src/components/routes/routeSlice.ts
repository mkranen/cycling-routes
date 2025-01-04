import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RouteType } from "../../types/route";

export const sports = {
    race_bike: "Race bike",
    mountain_bike: "Mountain bike",
    gravel_bike: "Gravel bike",
    touring_bike: "Touring bike",
    hike: "Hike",
    run: "Run",
};

export type Sport = "race_bike" | "mountain_bike" | "gravel_bike" | "touring_bike" | "hike" | "run" | null;

interface RouteState {
    selectedRoute: RouteType | null;
    limit: number;
    sport: Sport;
    minDistance: number | null;
    maxDistance: number | null;
}

const initialState: RouteState = {
    selectedRoute: null,
    limit: 200,
    sport: null,
    minDistance: 40,
    maxDistance: 60,
};

export const routeSlice = createSlice({
    name: "route",
    initialState,
    reducers: {
        setSelectedRoute: (state, action: PayloadAction<RouteType | null>) => {
            state.selectedRoute = action.payload;
        },
        setLimit: (state, action: PayloadAction<number>) => {
            state.limit = action.payload;
        },
        setSport: (state, action: PayloadAction<Sport>) => {
            state.sport = action.payload;
        },
        setMinDistance: (state, action: PayloadAction<number | null>) => {
            state.minDistance = action.payload;
        },
        setMaxDistance: (state, action: PayloadAction<number | null>) => {
            state.maxDistance = action.payload;
        },
    },
});

export const { setSelectedRoute, setLimit, setSport, setMinDistance, setMaxDistance } = routeSlice.actions;
export default routeSlice.reducer;
