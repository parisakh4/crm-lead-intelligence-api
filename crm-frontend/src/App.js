import React, { useEffect, useState } from "react";
import CompanyForm from "./CompanyForm";
import ContactForm from "./ContactForm";
import OpportunityForm from "./OpportunityForm";
import AiJobSearch from "./AiJobSearch";

const API = "http://127.0.0.1:5000";

const STAGE_BADGE = {
  "Wishlist":     "secondary",
  "Applied":      "primary",
  "Phone Screen": "warning",
  "Interview":    "warning",
  "Offer":        "success",
  "Rejected":     "danger",
};

function matches(query, ...fields) {
  if (!query.trim()) return true;
  const q = query.trim().toLowerCase();
  return fields.some(f => (f || "").toString().toLowerCase().includes(q));
}

function App() {
  const [companies, setCompanies] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [opportunities, setOpportunities] = useState([]);

  const [companyQuery, setCompanyQuery] = useState("");
  const [contactQuery, setContactQuery] = useState("");
  const [opportunityQuery, setOpportunityQuery] = useState("");
  const [opportunityStage, setOpportunityStage] = useState("");

  const [editingCompanyId, setEditingCompanyId] = useState(null);
  const [companyDraft, setCompanyDraft] = useState({});
  const [editingContactId, setEditingContactId] = useState(null);
  const [contactDraft, setContactDraft] = useState({});
  const [editingOpportunityId, setEditingOpportunityId] = useState(null);
  const [opportunityDraft, setOpportunityDraft] = useState({});
  const [editError, setEditError] = useState("");

  function loadCompanies() {
    fetch(`${API}/companies`).then(r => r.json()).then(setCompanies);
  }
  function loadContacts() {
    fetch(`${API}/contacts`).then(r => r.json()).then(setContacts);
  }
  function loadOpportunities() {
    fetch(`${API}/opportunities`).then(r => r.json()).then(setOpportunities);
  }

  useEffect(() => {
    loadCompanies();
    loadContacts();
    loadOpportunities();
  }, []);

  async function deleteRecord(endpoint, id, reload) {
    await fetch(`${API}/${endpoint}/${id}`, { method: "DELETE" });
    reload();
  }

  async function updateRecord(endpoint, id, payload, reload, onSuccess) {
    setEditError("");
    const res = await fetch(`${API}/${endpoint}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      setEditError(data.error || "Update failed");
      return;
    }
    reload();
    onSuccess();
  }

  function startEditCompany(c) {
    setEditError("");
    setEditingCompanyId(c.id);
    setCompanyDraft({ name: c.name, industry: c.industry, location: c.location, email: c.email });
  }
  function startEditContact(c) {
    setEditError("");
    setEditingContactId(c.id);
    setContactDraft({ name: c.name, email: c.email, phone: c.phone, company_id: c.company_id });
  }
  function startEditOpportunity(o) {
    setEditError("");
    setEditingOpportunityId(o.id);
    setOpportunityDraft({ name: o.name, stage: o.stage, value: o.value, company_id: o.company_id });
  }

  return (
    <div className="container py-4">
      <h1 className="mb-4">Job Search CRM</h1>

      {/* Companies */}
      <h2 className="h4 mb-3">Companies</h2>
      <CompanyForm onCreated={loadCompanies} />
      <input
        value={companyQuery}
        onChange={e => setCompanyQuery(e.target.value)}
        className="form-control mb-2"
        placeholder="Search companies by name, industry, or location..."
      />
      {editError && <div className="text-danger mb-2">{editError}</div>}
      <table className="table table-bordered table-hover mb-5">
        <thead className="table-dark">
          <tr>
            <th>Name</th>
            <th>Industry</th>
            <th>Location</th>
            <th>Email</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {companies
            .filter(c => matches(companyQuery, c.name, c.industry, c.location, c.email))
            .map(c => {
            const isEditing = editingCompanyId === c.id;
            return (
              <tr key={c.id}>
                {isEditing ? (
                  <>
                    <td><input className="form-control form-control-sm" value={companyDraft.name || ""}
                      onChange={e => setCompanyDraft({ ...companyDraft, name: e.target.value })} /></td>
                    <td><input className="form-control form-control-sm" value={companyDraft.industry || ""}
                      onChange={e => setCompanyDraft({ ...companyDraft, industry: e.target.value })} /></td>
                    <td><input className="form-control form-control-sm" value={companyDraft.location || ""}
                      onChange={e => setCompanyDraft({ ...companyDraft, location: e.target.value })} /></td>
                    <td><input className="form-control form-control-sm" value={companyDraft.email || ""}
                      onChange={e => setCompanyDraft({ ...companyDraft, email: e.target.value })} /></td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-success me-1"
                        onClick={() => updateRecord("companies", c.id, companyDraft, loadCompanies, () => setEditingCompanyId(null))}>
                        Save
                      </button>
                      <button className="btn btn-sm btn-outline-secondary"
                        onClick={() => setEditingCompanyId(null)}>
                        Cancel
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{c.name}</td>
                    <td>{c.industry}</td>
                    <td>{c.location}</td>
                    <td>{c.email}</td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-outline-primary me-1"
                        onClick={() => startEditCompany(c)}>
                        Edit
                      </button>
                      <button className="btn btn-sm btn-outline-danger"
                        onClick={() => deleteRecord("companies", c.id, loadCompanies)}>
                        Delete
                      </button>
                    </td>
                  </>
                )}
              </tr>
            );
          })}
          {companies.length === 0 && (
            <tr><td colSpan="5" className="text-muted">No companies yet.</td></tr>
          )}
        </tbody>
      </table>

      {/* Contacts */}
      <h2 className="h4 mb-3">Contacts</h2>
      <ContactForm companies={companies} onCreated={loadContacts} />
      <input
        value={contactQuery}
        onChange={e => setContactQuery(e.target.value)}
        className="form-control mb-2"
        placeholder="Search contacts by name, email, or company..."
      />
      <table className="table table-bordered table-hover mb-5">
        <thead className="table-dark">
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Company</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {contacts
            .filter(c => {
              const company = companies.find(co => co.id === c.company_id);
              return matches(contactQuery, c.name, c.email, c.phone, company && company.name);
            })
            .map(c => {
            const company = companies.find(co => co.id === c.company_id);
            const isEditing = editingContactId === c.id;
            return (
              <tr key={c.id}>
                {isEditing ? (
                  <>
                    <td><input className="form-control form-control-sm" value={contactDraft.name || ""}
                      onChange={e => setContactDraft({ ...contactDraft, name: e.target.value })} /></td>
                    <td><input className="form-control form-control-sm" value={contactDraft.email || ""}
                      onChange={e => setContactDraft({ ...contactDraft, email: e.target.value })} /></td>
                    <td><input className="form-control form-control-sm" value={contactDraft.phone || ""}
                      onChange={e => setContactDraft({ ...contactDraft, phone: e.target.value })} /></td>
                    <td>
                      <select className="form-select form-select-sm" value={contactDraft.company_id || ""}
                        onChange={e => setContactDraft({ ...contactDraft, company_id: parseInt(e.target.value) })}>
                        {companies.map(co => (
                          <option key={co.id} value={co.id}>{co.name}</option>
                        ))}
                      </select>
                    </td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-success me-1"
                        onClick={() => updateRecord("contacts", c.id, contactDraft, loadContacts, () => setEditingContactId(null))}>
                        Save
                      </button>
                      <button className="btn btn-sm btn-outline-secondary"
                        onClick={() => setEditingContactId(null)}>
                        Cancel
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{c.name}</td>
                    <td>{c.email}</td>
                    <td>{c.phone}</td>
                    <td>{company ? company.name : c.company_id}</td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-outline-primary me-1"
                        onClick={() => startEditContact(c)}>
                        Edit
                      </button>
                      <button className="btn btn-sm btn-outline-danger"
                        onClick={() => deleteRecord("contacts", c.id, loadContacts)}>
                        Delete
                      </button>
                    </td>
                  </>
                )}
              </tr>
            );
          })}
          {contacts.length === 0 && (
            <tr><td colSpan="5" className="text-muted">No contacts yet.</td></tr>
          )}
        </tbody>
      </table>

      {/* Opportunities */}
      <h2 className="h4 mb-3">Opportunities</h2>
      <AiJobSearch onAdded={() => { loadOpportunities(); loadCompanies(); }} />
      <OpportunityForm companies={companies} onCreated={loadOpportunities} />
      <div className="row g-2 mb-2">
        <div className="col-md-9">
          <input
            value={opportunityQuery}
            onChange={e => setOpportunityQuery(e.target.value)}
            className="form-control"
            placeholder="Search opportunities by role or company..."
          />
        </div>
        <div className="col-md-3">
          <select
            value={opportunityStage}
            onChange={e => setOpportunityStage(e.target.value)}
            className="form-select"
          >
            <option value="">All stages</option>
            {Object.keys(STAGE_BADGE).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>
      <table className="table table-bordered table-hover mb-5">
        <thead className="table-dark">
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>Stage</th>
            <th>Value</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {opportunities
            .filter(o => !opportunityStage || o.stage === opportunityStage)
            .filter(o => {
              const company = companies.find(c => c.id === o.company_id);
              return matches(opportunityQuery, o.name, company && company.name);
            })
            .map(o => {
            const company = companies.find(c => c.id === o.company_id);
            const isEditing = editingOpportunityId === o.id;
            return (
              <tr key={o.id}>
                {isEditing ? (
                  <>
                    <td><input className="form-control form-control-sm" value={opportunityDraft.name || ""}
                      onChange={e => setOpportunityDraft({ ...opportunityDraft, name: e.target.value })} /></td>
                    <td>
                      <select className="form-select form-select-sm" value={opportunityDraft.company_id || ""}
                        onChange={e => setOpportunityDraft({ ...opportunityDraft, company_id: parseInt(e.target.value) })}>
                        {companies.map(co => (
                          <option key={co.id} value={co.id}>{co.name}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <select className="form-select form-select-sm" value={opportunityDraft.stage || ""}
                        onChange={e => setOpportunityDraft({ ...opportunityDraft, stage: e.target.value })}>
                        {Object.keys(STAGE_BADGE).map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td><input type="number" className="form-control form-control-sm" value={opportunityDraft.value ?? ""}
                      onChange={e => setOpportunityDraft({ ...opportunityDraft, value: e.target.value ? parseFloat(e.target.value) : null })} /></td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-success me-1"
                        onClick={() => updateRecord("opportunities", o.id, opportunityDraft, loadOpportunities, () => setEditingOpportunityId(null))}>
                        Save
                      </button>
                      <button className="btn btn-sm btn-outline-secondary"
                        onClick={() => setEditingOpportunityId(null)}>
                        Cancel
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{o.name}</td>
                    <td>{company ? company.name : o.company_id}</td>
                    <td>
                      <span className={`badge bg-${STAGE_BADGE[o.stage] || "secondary"}`}>
                        {o.stage}
                      </span>
                    </td>
                    <td>{o.value ? `$${o.value}` : "—"}</td>
                    <td className="text-nowrap">
                      <button className="btn btn-sm btn-outline-primary me-1"
                        onClick={() => startEditOpportunity(o)}>
                        Edit
                      </button>
                      <button className="btn btn-sm btn-outline-danger"
                        onClick={() => deleteRecord("opportunities", o.id, loadOpportunities)}>
                        Delete
                      </button>
                    </td>
                  </>
                )}
              </tr>
            );
          })}
          {opportunities.length === 0 && (
            <tr><td colSpan="5" className="text-muted">No opportunities yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
