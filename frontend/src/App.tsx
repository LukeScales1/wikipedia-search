import React from 'react';
import logo from './logo.svg';
import './App.scss';
import { Articles } from "./features/articles/Articles";
import { Search } from "./features/search/Search";
import { useGetArticlesQuery, usePostArticlesMutation, useGetSearchResultsQuery } from "./redux/apiSlice";


function App() {
  const [searchTerms, setSearchTerms] = React.useState<string>("");

  const {
    data: articles = [],
    error: articlesError,
    isLoading: isLoadingArticles,
  } = useGetArticlesQuery('');
  const {
    data: searchResults = [],
    error: searchResultsError,
    isLoading: isLoadingSearchResults,
  } = useGetSearchResultsQuery(searchTerms);
  const [
    updateArticles,
    { isLoading: isUpdating },
  ] = usePostArticlesMutation();

  const isSearchingDisabled = !!articlesError || isLoadingArticles || !!searchResultsError || isLoadingSearchResults;

  return (
    <div className="App">
      <div className="logoContainer">
        <img src={logo} alt="logo" onClick={() => updateArticles(null)} />
        <p><i>Click the react logo to load more articles</i>☝️!</p>
      </div>
      <Search
        updateSearchTerms={setSearchTerms}
        isSearchingDisabled={isSearchingDisabled}
      />
      <Articles
        articles={articles}
        searchResults={searchResults}
        isLoading={isLoadingArticles}
        isError={!!articlesError}
      />
    </div>
  );
}

export default App;
