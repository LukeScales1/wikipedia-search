import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Articles } from "./features/articles/Articles";
import { Search } from "./features/search/Search";
import { useGetArticlesQuery, useGetSearchResultsQuery } from "./redux/apiSlice";


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

  const isSearchingDisabled = !!articlesError || isLoadingArticles || !!searchResultsError || isLoadingSearchResults;

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
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
      </header>
    </div>
  );
}

export default App;
