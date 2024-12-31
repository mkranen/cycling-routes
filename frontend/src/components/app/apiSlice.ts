import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const routesApi = createApi({
    reducerPath: "pokemonApi",
    baseQuery: fetchBaseQuery({ baseUrl: "http://localhost:8081" }),
    endpoints: (builder) => ({
        getKomootRoute: builder.query<any, any>({
            query: (id) => `komoot-route/${id}`,
        }),
        getKomootRoutes: builder.query<any, any>({
            query: ({ limit }) => (limit ? `komoot-routes?limit=${limit}` : "komoot-routes"),
        }),
    }),
});

export const { useGetKomootRouteQuery, useGetKomootRoutesQuery } = routesApi;
