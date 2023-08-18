import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Articles } from "./features/articles/Articles";


function App() {

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Articles />
      </header>
    </div>
  );
}

export default App;
