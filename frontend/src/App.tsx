import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Articles } from "./features/articles/Articles";
import { Search } from "./features/search/Search";


function App() {

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Search />
        <Articles />
      </header>
    </div>
  );
}

export default App;
