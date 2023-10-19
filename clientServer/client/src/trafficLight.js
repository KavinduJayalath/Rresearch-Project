import Light from "./Light";
// import { useTrafficLight } from "react-hooks-helper";
import React, { useState, useEffect } from "react";
import axios from 'axios';
import "./styles.css";

const lightDurations = [3000, 2000, 1000];

const TrafficLight = () => {
  const [colorIndex, setColorIndex] = useState(1);

  const active = async (col) => {
    setColorIndex(col);
    if (col === 0) {
      axios.get('http://localhost:8060/light/set/r')
      .then(response => {
        const data = response.data;
        alert(data);
      })
      .catch(error => {
        console.error("Error making the API request:", error);
      });
    }
    if (col === 2) {
      axios.get('http://localhost:8060/light/set/y')
      .then(response => {
        const data = response.data;
        alert(data);
      })
      .catch(error => {
        console.error("Error making the API request:", error);
      });
    }
    if (col === 1) {
      axios.get('http://localhost:8060/light/set/g')
      .then(response => {
        const data = response.data;
        alert(data);
      })
      .catch(error => {
        console.error("Error making the API request:", error);
      });
    }
  };

  return (
    <div className="App">
        <h1></h1>
        <h1></h1>
        <h1></h1>
      <h1>Traffic Lights for Vehicles</h1>
        <div className="traffic-light">
            <button onClick={() => active(0)}>
            <Light color="#f00" active={colorIndex === 0} />
            </button>
            <button onClick={() => active(2)}>
            <Light color="#ff0" active={colorIndex === 2} />
            </button>
            <button onClick={() => active(1)}>
            <Light color="#0c0" active={colorIndex === 1} />
            </button>
        </div>
    </div>
  );
};

export default TrafficLight;
