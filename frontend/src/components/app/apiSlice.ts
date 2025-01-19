import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const routesApi = createApi({
    reducerPath: "routes",
    baseQuery: fetchBaseQuery({ baseUrl: "http://localhost:8081" }),
    endpoints: (builder) => ({
        getRoute: builder.query<any, any>({
            query: (id) => `route/${id}`,
        }),
        getRoutes: builder.query<any, any>({
            query: ({ sport, collections, minDistance, maxDistance, mapBounds, limit }) => {
                const params = new URLSearchParams();
                if (sport) params.append("sport", sport.value);
                if (collections) params.append("collections", collections);
                if (minDistance) params.append("min_distance", minDistance);
                if (maxDistance) params.append("max_distance", maxDistance);
                if (mapBounds) params.append("min_bounds", mapBounds[0]);
                if (mapBounds) params.append("max_bounds", mapBounds[1]);
                if (limit) params.append("limit", limit);

                const queryString = params.toString();
                return params.size > 0 ? `routes?${queryString}` : "routes";
            },
        }),
        getKomootRoute: builder.query<any, any>({
            query: (id) => `komoot-route/${id}`,
        }),
        getKomootRoutes: builder.query<any, any>({
            query: ({ limit }) => (limit ? `komoot-routes?limit=${limit}` : "komoot-routes"),
        }),
    }),
});

export const { useGetRouteQuery, useGetRoutesQuery, useGetKomootRouteQuery, useGetKomootRoutesQuery } = routesApi;
