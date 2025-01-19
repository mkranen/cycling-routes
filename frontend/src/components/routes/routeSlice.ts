import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RouteType } from "../../types/route";

export const sports = [
    { value: "race_bike", label: "Race bike" },
    { value: "mountain_bike", label: "Mountain bike" },
    { value: "gravel_bike", label: "Gravel bike" },
    { value: "touring_bike", label: "Touring bike" },
    { value: "hike", label: "Hike" },
    { value: "run", label: "Run" },
];

export const collections = [
    { value: "personal", label: "Personal" },
    { value: "gravelritten", label: "Gravelritten" },
    { value: "gijs_bruinsma", label: "Gijs Bruinsma" },
];

export type Sport = { value: string; label: string } | null;

interface RouteState {
    selectedRoute: RouteType | null;
    previousSelectedRoute: RouteType | null;
    limit: number;
    sport: Sport | null;
    minDistance: number | null;
    maxDistance: number | null;
    selectedCollections?: { value: string; label: string }[];
}

const initialState: RouteState = {
    selectedRoute: null,
    previousSelectedRoute: null,
    limit: 200,
    sport: sports[0],
    minDistance: 40,
    maxDistance: 60,
    selectedCollections: [collections[0]],
};

export const routeSlice = createSlice({
    name: "route",
    initialState,
    reducers: {
        setSelectedRoute: (state, action: PayloadAction<RouteType | null>) => {
            state.selectedRoute = action.payload;
        },
        setPreviousSelectedRoute: (state, action: PayloadAction<RouteType | null>) => {
            state.previousSelectedRoute = action.payload;
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
        setSelectedCollections: (state, action: PayloadAction<{ value: string; label: string }[]>) => {
            state.selectedCollections = action.payload;
        },
    },
});

export const {
    setSelectedRoute,
    setPreviousSelectedRoute,
    setLimit,
    setSport,
    setMinDistance,
    setMaxDistance,
    setSelectedCollections,
} = routeSlice.actions;
export default routeSlice.reducer;
