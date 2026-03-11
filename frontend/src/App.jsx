import React, { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus("");
    setSummary("");

    if (!file) {
      setStatus("Please select a CSV file.");
      return;
    }

    if (!email) {
      setStatus("Please enter an email address.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setStatus(data.message);
      setSummary(data.summary);
    } catch (error) {
      setStatus(error.message || "Failed to connect to backend.");
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Sales Insight Automator</h1>
        <p>Upload your sales CSV and receive an executive summary.</p>
      </header>

      <main className="card">
        <form onSubmit={handleSubmit} className="form">

          <label className="field">
            <span>Sales CSV File</span>
            <input type="file" accept=".csv" onChange={handleFileChange} />
          </label>

          <label className="field">
            <span>Destination Email</span>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <button className="submit-button" disabled={loading}>
            {loading ? "Processing..." : "Generate Summary"}
          </button>
        </form>

        {status && <div className="status">{status}</div>}

        {summary && (
          <div className="summary-box">
            <h3>Executive Summary</h3>
            <pre>{summary}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;