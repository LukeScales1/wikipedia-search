import React from 'react'
import type { RootState } from '../../redux/store'
import { useAppSelector } from '../../redux/hooks'
import { Article } from "../../types/article";


export const Articles = () => {
  const articles: Article[] = useAppSelector((state: RootState) => state.article.articles)

  return (
    <div>
      {articles.map((article: Article) => (
        <div>
          <h3>{article.title}</h3>
        </div>
      ))}
    </div>
  )
}
