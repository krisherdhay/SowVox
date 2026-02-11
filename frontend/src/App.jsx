import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState("Connecting to backend...")

  // This grabs the Railway URL you set in Netlify
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  useEffect(() => {
    // This 'calls' your FastAPI backend on Railway
    fetch(API_URL)
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage("Error: Could not reach SowVox Brain"))
  }, [API_URL])

  return (
    <div className="App">
      <header className="header">
        <h1>🐖 SowVox Dashboard</h1>
        <div className="status-badge">
          System: <strong>{message}</strong>
        </div>
      </header>
      
      <main className="content">
        <div className="card">
          <h2>Live Sensor Stream</h2>
          <p>Connected to: <code>{API_URL}</code></p>
          <hr />
          <p>Waiting for the first weigh-in from the Nedap feeders...</p>
        </div>
      </main>
    </div>
  )
}

export default App