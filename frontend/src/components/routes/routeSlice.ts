import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export const sports = {
    race_bike: "Race bike",
    mountain_bike: "Mountain bike",
    gravel_bike: "Gravel bike",
    touring_bike: "Touring bike",
    hike: "Hike",
    run: "Run",
};

export type Sport = "race_bike" | "mountain_bike" | "gravel_bike" | "touring_bike" | "hike" | "run" | null;

interface Route {
    limit: number;
    sport: Sport;
    minDistance: number | null;
    maxDistance: number | null;
}

const initialState: Route = {
    limit: 100,
    sport: null,
    minDistance: 40,
    maxDistance: 60,
};

export const routeSlice = createSlice({
    name: "route",
    initialState,
    reducers: {
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

export const { setLimit, setSport, setMinDistance, setMaxDistance } = routeSlice.actions;
export default routeSlice.reducer;
