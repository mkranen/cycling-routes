import { createListenerMiddleware } from "@reduxjs/toolkit";
import { RootState } from "../app/store";
import { setPreviousSelectedRoute, setSelectedRoute } from "../components/routes/routeSlice";

export const routeListenerMiddleware = createListenerMiddleware();

routeListenerMiddleware.startListening({
    actionCreator: setSelectedRoute,
    effect: async (action, listenerApi) => {
        const originalRootState = listenerApi.getOriginalState() as RootState;
        listenerApi.dispatch(setPreviousSelectedRoute(originalRootState.route.selectedRoute));
    },
});
