import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Articles } from "./features/articles/Articles";
import { Search } from "./features/search/Search";


function App() {
  const [searchTerms, setSearchTerms] = React.useState<string>("");
  const searchTermUpdate = (searchTerms: string) => setSearchTerms(searchTerms);
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Search
          updateSearchTerms={searchTermUpdate}
        />
        <Articles
          searchTerms={searchTerms}
        />
      </header>
    </div>
  );
}

export default App;
