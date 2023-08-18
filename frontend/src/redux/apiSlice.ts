import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { Article, SearchResult } from "../types";

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:8000' }),
  endpoints: builder => ({
    getArticles: builder.query<Article[], string>({
      query: () => '/articles'
    }),
    getSearchResults: builder.query<SearchResult[], string>({
      query: (searchTerms: string) => `/search?query=${searchTerms}`
    }),
  })
})

export const { useGetArticlesQuery, useGetSearchResultsQuery } = apiSlice
