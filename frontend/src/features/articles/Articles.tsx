import React from 'react'
import {Article, SearchResult } from "../../types";

import { useGetArticlesQuery, useGetSearchResultsQuery } from "../../redux/apiSlice";
import { Spinner } from "@chakra-ui/react";


const formatWikipediaUrl = (title: string) => {
  const formattedTitle = title.replace(/ /g, "_");
  return `https://en.wikipedia.org/wiki/${formattedTitle}`;
};

type Props = {
  searchTerms: string;
}


export const Articles: React.FC<Props> = ({searchTerms}) => {
  const { data: articles = [], error, isLoading} = useGetArticlesQuery('');
  const { data: searchResults = [] } = useGetSearchResultsQuery(searchTerms);

  const matchingArticleTitles = searchResults.map((searchResult: SearchResult) => searchResult.title);
  const isArticleInResults = (article: Article) => matchingArticleTitles.includes(article.title);

  return (
    <div>
      { error ?
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
                  <div key={article.title} style={includeArticle ? {cursor: "pointer"} : {opacity: "25%"}}>
                    <h3 onClick={() => includeArticle &&
                      window.open(formatWikipediaUrl(article.title), "_blank", "noreferrer")}
                    >
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
