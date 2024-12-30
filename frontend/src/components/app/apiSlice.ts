import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const routesApi = createApi({
    reducerPath: "pokemonApi",
    baseQuery: fetchBaseQuery({ baseUrl: "http://localhost:8081" }),
    endpoints: (builder) => ({
        getRoute: builder.query<any, any>({
            query: (name) => `routes/${name}`,
        }),
        getRoutes: builder.query<any, any>({
            query: ({ limit }) => (limit ? `routes?limit=${limit}` : "routes"),
        }),
    }),
});

export const { useGetRouteQuery, useGetRoutesQuery } = routesApi;
