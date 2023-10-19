import './App.css';
import React, { createContext, useReducer } from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Files from './files';
import Lights from './trafficLight';

export const UserContext = createContext();

function App() {

  return (
    <div>
      <Router>
        <Routes>
          <Route path='/light' element={<Lights />} />
          <Route path='/' element={<Files />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
