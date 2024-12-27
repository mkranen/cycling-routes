import { combineReducers, configureStore } from "@reduxjs/toolkit";
import mapSlice from "./components/map/mapSlice";

const combinedReducer = combineReducers({
  map: mapSlice,
});

export type RootState = ReturnType<typeof combinedReducer>;

const store = configureStore({
  reducer: combinedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: { warnAfter: 256 },
    }),
});

export default store;
export type AppDispatch = typeof store.dispatch;
