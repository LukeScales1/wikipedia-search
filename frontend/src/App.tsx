import React from 'react';
import logo from './logo.svg';
import './App.css';
import { getArticles } from "./apiInterface";
import { Articles } from "./features/articles/Articles";
import { useAppDispatch } from "./redux/hooks";
import { replace } from "./features/articles/articleSlice";


function App() {

  const dispatch = useAppDispatch();
  const fetchArticles = async () => {
    try {
      const getCurrentArticles = await getArticles();
      dispatch(replace(getCurrentArticles?.data));
    } catch (error) {
      console.error(error);
    }
  };

  fetchArticles();

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Articles />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
