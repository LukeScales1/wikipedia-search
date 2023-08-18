import React from 'react'
import {Article, SearchResult } from "../../types";

import { useGetArticlesQuery, useGetSearchResultsQuery } from "../../redux/apiSlice";


const formatWikipediaUrl = (title: string) => {
  const formattedTitle = title.replace(/ /g, "_");
  return `https://en.wikipedia.org/wiki/${formattedTitle}`;
};

export const Articles = () => {
  const { data: articles = [] } = useGetArticlesQuery('');
  const { data: searchResults = [] } = useGetSearchResultsQuery('');

  const matchingArticleTitles = searchResults.map((searchResult: SearchResult) => searchResult.title);
  const isArticleInResults = (article: Article) => matchingArticleTitles.includes(article.title);

  return (
    <div>
      {articles.map((article: Article) => {
        const includeArticle = isArticleInResults(article);
        return (
          <div key={article.title} style={includeArticle ? {cursor: "pointer"} : {opacity: "25%"}}>
            <h3 onClick={() => includeArticle &&
              window.open(formatWikipediaUrl(article.title), "_blank", "noreferrer")}
            >
              {article.title }
            </h3>
          </div>
        )
      })}
    </div>
  )
}
