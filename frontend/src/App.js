import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [status, setStatus] = useState("loading");
  const [isRunning, setIsRunning] = useState(false);

  const API_BASE = "http://127.0.0.1:5000";

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/status`);
      setIsRunning(res.data.running);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
    }
  };

  const startBot = async () => {
    setStatus("starting...");
    await axios.post(`${API_BASE}/start`);
    fetchStatus();
  };

  const stopBot = async () => {
    setStatus("stopping...");
    await axios.post(`${API_BASE}/stop`);
    fetchStatus();
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="App">
      <h1>📈 MT5 Trading Bot Dashboard</h1>
      <p>Status: <strong>{isRunning ? "🟢 Running" : "🔴 Stopped"}</strong></p>

      <div className="buttons">
        <button onClick={startBot} disabled={isRunning}>▶️ Start Bot</button>
        <button onClick={stopBot} disabled={!isRunning}>⏹ Stop Bot</button>
      </div>

      {status === "error" && (
        <p style={{ color: "red" }}>⚠️ Cannot connect to backend (Flask not running?)</p>
      )}
    </div>
  );
}

export default App;
