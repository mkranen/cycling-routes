import React, { useMemo } from "react";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { RouteType } from "../../types/route";
import { setSelectedRoute } from "./routeSlice";

export default function Route() {
    const selectedRoute: RouteType | null = useAppSelector((state) => state.route.selectedRoute);
    const dispatch = useAppDispatch();

    const url = useMemo(() => {
        if (!selectedRoute) return "";

        let url = "";
        if (selectedRoute.komoot) {
            url = `https://www.komoot.com/tour/${selectedRoute.komoot.id}`;
        } else if (selectedRoute.strava) {
            url = `https://www.strava.com/routes/${selectedRoute.strava.id}`;
        }
        return url;
    }, [selectedRoute]);

    if (!selectedRoute) {
        return null;
    }

    return (
        <div className="shadow-xl card card-compact bg-base-100 w-96">
            <div className="absolute justify-end right-2 top-2">
                <button className="btn btn-square btn-sm btn-ghost" onClick={() => dispatch(setSelectedRoute(null))}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-6 h-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div className="card-body">
                <div className="flex flex-col gap-0">
                    <h2 className="pb-0 m-0 card-title">{selectedRoute.name}</h2>

                    {selectedRoute.distance && (
                        <p className="text-lg text-gray-500">{(selectedRoute.distance / 1000).toFixed(2)} km</p>
                    )}
                </div>
                <div className="flex flex-row items-end justify-between card-actions">
                    <button className="btn btn-primary" onClick={() => window.open(url, "_blank")}>
                        Show on {selectedRoute.source}
                    </button>
                    <div className={`text-sm ${selectedRoute.source === "Komoot" ? "text-komoot" : "text-strava"}`}>
                        {selectedRoute.source}
                    </div>
                </div>
            </div>
        </div>
    );
}
