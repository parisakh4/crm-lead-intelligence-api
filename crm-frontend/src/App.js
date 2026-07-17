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

function App() {
  const [companies, setCompanies] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [opportunities, setOpportunities] = useState([]);

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

  return (
    <div className="container py-4">
      <h1 className="mb-4">Job Search CRM</h1>

      {/* Companies */}
      <h2 className="h4 mb-3">Companies</h2>
      <CompanyForm onCreated={loadCompanies} />
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
          {companies.map(c => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.industry}</td>
              <td>{c.location}</td>
              <td>{c.email}</td>
              <td>
                <button className="btn btn-sm btn-outline-danger"
                  onClick={() => deleteRecord("companies", c.id, loadCompanies)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
          {companies.length === 0 && (
            <tr><td colSpan="5" className="text-muted">No companies yet.</td></tr>
          )}
        </tbody>
      </table>

      {/* Contacts */}
      <h2 className="h4 mb-3">Contacts</h2>
      <ContactForm companies={companies} onCreated={loadContacts} />
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
          {contacts.map(c => {
            const company = companies.find(co => co.id === c.company_id);
            return (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.email}</td>
                <td>{c.phone}</td>
                <td>{company ? company.name : c.company_id}</td>
                <td>
                  <button className="btn btn-sm btn-outline-danger"
                    onClick={() => deleteRecord("contacts", c.id, loadContacts)}>
                    Delete
                  </button>
                </td>
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
          {opportunities.map(o => {
            const company = companies.find(c => c.id === o.company_id);
            return (
              <tr key={o.id}>
                <td>{o.name}</td>
                <td>{company ? company.name : o.company_id}</td>
                <td>
                  <span className={`badge bg-${STAGE_BADGE[o.stage] || "secondary"}`}>
                    {o.stage}
                  </span>
                </td>
                <td>{o.value ? `$${o.value}` : "—"}</td>
                <td>
                  <button className="btn btn-sm btn-outline-danger"
                    onClick={() => deleteRecord("opportunities", o.id, loadOpportunities)}>
                    Delete
                  </button>
                </td>
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
