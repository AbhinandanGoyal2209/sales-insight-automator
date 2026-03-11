import React, { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus("");

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

      setStatus(data.message || "Summary generated and email sent.");
    } catch (error) {
      setStatus(error.message || "An error occurred while uploading.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Sales Insight Automator</h1>
        <p>Upload your sales CSV and receive an executive summary by email.</p>
      </header>

      <main className="card">
        <form onSubmit={handleSubmit} className="form">
          <label className="field">
            <span>Sales CSV file</span>
            <input type="file" accept=".csv" onChange={handleFileChange} />
          </label>

          <label className="field">
            <span>Destination email</span>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? "Processing..." : "Generate Summary"}
          </button>
        </form>

        {status && <div className="status">{status}</div>}
      </main>
    </div>
  );
}

export default App;

