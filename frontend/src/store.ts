import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { routesApi } from "./components/app/apiSlice";
import mapSlice from "./components/map/mapSlice";

const combinedReducer = combineReducers({
    map: mapSlice,
    [routesApi.reducerPath]: routesApi.reducer,
});

export type RootState = ReturnType<typeof combinedReducer>;

const store = configureStore({
    reducer: combinedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: false,
            immutableCheck: { warnAfter: 256 },
        }).concat(routesApi.middleware),
});

export default store;
export type AppDispatch = typeof store.dispatch;
