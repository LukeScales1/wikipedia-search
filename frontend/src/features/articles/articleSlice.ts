import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { Article } from "../../types";

export interface ArticleState {
  articles: Article[];
}

const initialState: ArticleState = {
  articles: [],
}

export const articleSlice = createSlice({
  name: 'articles',
  initialState,
  reducers: {
    update: (state, action) => {
      state.articles = [...state.articles, ...action.payload.articles]
    },
    clear: (state) => {
      state.articles = []
    },
    replace: (state, action: PayloadAction<Article[]>) => {
      state.articles = action.payload
    },
  },
})

export const { update, clear, replace } = articleSlice.actions

export default articleSlice.reducer
