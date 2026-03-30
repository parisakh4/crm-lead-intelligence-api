import React, { useState } from "react";

const API = "http://127.0.0.1:5000";

const STAGES = ["Wishlist", "Applied", "Phone Screen", "Interview", "Offer", "Rejected"];

function OpportunityForm({ companies, onCreated }) {
  const [form, setForm] = useState({ name: "", stage: "", value: "", company_id: "" });
  const [error, setError] = useState("");

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const res = await fetch(`${API}/opportunities`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        company_id: parseInt(form.company_id),
        value: form.value ? parseFloat(form.value) : null,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.error);
      return;
    }

    setForm({ name: "", stage: "", value: "", company_id: "" });
    onCreated();
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="row g-2">
        <div className="col-md-3">
          <input name="name" value={form.name} onChange={handleChange}
            className="form-control" placeholder="Role / Position *" required />
        </div>
        <div className="col-md-2">
          <select name="stage" value={form.stage} onChange={handleChange}
            className="form-select" required>
            <option value="">Stage *</option>
            {STAGES.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div className="col-md-2">
          <input name="value" value={form.value} onChange={handleChange}
            className="form-control" placeholder="Salary" type="number" />
        </div>
        <div className="col-md-3">
          <select name="company_id" value={form.company_id} onChange={handleChange}
            className="form-select" required>
            <option value="">Select company *</option>
            {companies.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="col-md-2">
          <button type="submit" className="btn btn-primary w-100">Add</button>
        </div>
      </div>
      {error && <div className="text-danger mt-2">{error}</div>}
    </form>
  );
}

export default OpportunityForm;
