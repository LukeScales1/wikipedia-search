import React from 'react'
import { Article, SearchResult } from "../../types";
import { Spinner } from "@chakra-ui/react";


type Props = {
  articles: Article[];
  searchResults: SearchResult[];
  isLoading: boolean;
  isError: boolean;
}

const formatWikipediaUrl = (title: string) => {
  const formattedTitle = title.replace(/ /g, "_");
  return `https://en.wikipedia.org/wiki/${formattedTitle}`;
};

const openWikipediaArticle = (title: string) => {
  window.open(formatWikipediaUrl(title), "_blank", "noreferrer");
};

const getArticleStyle = (isArticleSelected: boolean) => {
  return isArticleSelected ? { cursor: "pointer" } : { opacity: "25%" };
}

export const Articles: React.FC<Props> = ({articles, searchResults, isLoading, isError}) => {

  const matchingArticleTitles = searchResults.map((searchResult: SearchResult) => searchResult.title);
  const isArticleInResults = (article: Article) => matchingArticleTitles.includes(article.title);

  return (
    <div>
      { isError ?
        (
          <>
            <div>Oh no, there was an error loading your articles!</div>
            <div>Please refresh your browser</div>
          </>
        ) : (
          isLoading ?
            (
              <>
                <div>Loading your random Wikipedia articles...</div>
                <Spinner size='xl' />
              </>
            ) : (
              articles?.map((article: Article) => {
                const includeArticle = isArticleInResults(article);
                return (
                  <div key={article.title} style={getArticleStyle(includeArticle)}>
                    <h3 onClick={() => includeArticle && openWikipediaArticle(article.title)}>
                      { article.title }
                    </h3>
                  </div>
                )
              })
            )
        )
      }
    </div>
  )
}
