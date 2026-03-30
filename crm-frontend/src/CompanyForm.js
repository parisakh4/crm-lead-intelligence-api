import React, { useState } from "react";

const API = "http://127.0.0.1:5000";

function CompanyForm({ onCreated }) {
  const [form, setForm] = useState({ name: "", industry: "", location: "", email: "" });
  const [error, setError] = useState("");

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const res = await fetch(`${API}/companies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.error);
      return;
    }

    setForm({ name: "", industry: "", location: "", email: "" });
    onCreated();
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="row g-2">
        <div className="col-md-3">
          <input name="name" value={form.name} onChange={handleChange}
            className="form-control" placeholder="Name *" required />
        </div>
        <div className="col-md-3">
          <input name="industry" value={form.industry} onChange={handleChange}
            className="form-control" placeholder="Industry" />
        </div>
        <div className="col-md-2">
          <input name="location" value={form.location} onChange={handleChange}
            className="form-control" placeholder="Location" />
        </div>
        <div className="col-md-3">
          <input name="email" value={form.email} onChange={handleChange}
            className="form-control" placeholder="Email" />
        </div>
        <div className="col-md-1">
          <button type="submit" className="btn btn-primary w-100">Add</button>
        </div>
      </div>
      {error && <div className="text-danger mt-2">{error}</div>}
    </form>
  );
}

export default CompanyForm;
