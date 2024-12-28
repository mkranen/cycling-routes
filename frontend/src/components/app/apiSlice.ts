import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import humps from "humps";

export const routesApi = createApi({
    reducerPath: "pokemonApi",
    baseQuery: fetchBaseQuery({ baseUrl: "http://localhost:8081" }),
    endpoints: (builder) => ({
        getRoute: builder.query<any, any>({
            query: (name) => `routes/${name}`,
        }),
        getRoutes: builder.query<any, any>({
            query: () => "routes",
            transformResponse: (response: any) => {
                return humps.camelizeKeys(response);
            },
        }),
    }),
});

export const { useGetRouteQuery, useGetRoutesQuery } = routesApi;
