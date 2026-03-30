import React, { useState } from "react";

const API = "http://127.0.0.1:5000";

function ContactForm({ companies, onCreated }) {
  const [form, setForm] = useState({ name: "", email: "", phone: "", company_id: "" });
  const [error, setError] = useState("");

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const res = await fetch(`${API}/contacts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, company_id: parseInt(form.company_id) }),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.error);
      return;
    }

    setForm({ name: "", email: "", phone: "", company_id: "" });
    onCreated();
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="row g-2">
        <div className="col-md-3">
          <input name="name" value={form.name} onChange={handleChange}
            className="form-control" placeholder="Name *" required />
        </div>
        <div className="col-md-2">
          <input name="email" value={form.email} onChange={handleChange}
            className="form-control" placeholder="Email" />
        </div>
        <div className="col-md-2">
          <input name="phone" value={form.phone} onChange={handleChange}
            className="form-control" placeholder="Phone" />
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

export default ContactForm;
