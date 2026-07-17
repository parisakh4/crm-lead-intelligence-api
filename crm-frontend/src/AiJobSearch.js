import React, { useState } from "react";

const API = "http://127.0.0.1:5000";

function AiJobSearch({ onAdded }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function handleSearch(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const res = await fetch(`${API}/opportunities/ai-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 5 }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error);
        return;
      }

      setResult(data);
      onAdded();
    } catch (err) {
      setError("Request failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card mb-4">
      <div className="card-body">
        <h3 className="h6 mb-2">AI Job Search</h3>
        <form onSubmit={handleSearch} className="row g-2">
          <div className="col-md-9">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="form-control"
              placeholder="e.g. backend engineer, remote, entry level"
              required
            />
          </div>
          <div className="col-md-3">
            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? "Searching..." : "Search & Add"}
            </button>
          </div>
        </form>

        {error && <div className="text-danger mt-2">{error}</div>}

        {result && (
          <div className="mt-2 small">
            <div className="text-success">
              Added {result.count_added} opportunit{result.count_added === 1 ? "y" : "ies"}.
            </div>
            {result.skipped_duplicates.length > 0 && (
              <div className="text-muted">
                Skipped {result.skipped_duplicates.length} already in your CRM.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AiJobSearch;
