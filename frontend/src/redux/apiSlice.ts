import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { Article, SearchResult } from "../types";

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: process.env.REACT_APP_WIKI_API_URL }),
  tagTypes: ['Articles'],
  endpoints: builder => ({
    getArticles: builder.query<Article[], string>({
      query: () => '/articles',
      providesTags: (result: Article[] | undefined) =>
        result ? [
          ...result.map(({ title }) => (
            { type: 'Articles', title } as const)
          ),
            { type: 'Articles', id: 'LIST' },
          ]
            :
          [{ type: 'Articles', id: 'LIST' }],
    }),
    postArticles: builder.mutation({
      query: () => ({
        url: '/articles',
        method: 'POST',
      }),
      invalidatesTags: [{ type: 'Articles', id: 'LIST' }],
    }),
    getSearchResults: builder.query<SearchResult[], string>({
      query: (searchTerms: string) => `/search?query=${searchTerms}`
    }),
  })
})

export const { useGetArticlesQuery, usePostArticlesMutation, useGetSearchResultsQuery } = apiSlice
