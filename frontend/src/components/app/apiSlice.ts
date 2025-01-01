import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const routesApi = createApi({
    reducerPath: "pokemonApi",
    baseQuery: fetchBaseQuery({ baseUrl: "http://localhost:8081" }),
    endpoints: (builder) => ({
        getRoute: builder.query<any, any>({
            query: (id) => `route/${id}`,
        }),
        getRoutes: builder.query<any, any>({
            query: ({ limit }) => (limit ? `routes?limit=${limit}` : "routes"),
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
