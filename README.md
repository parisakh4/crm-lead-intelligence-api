# Job Search CRM

A personal CRM for managing a job search — track companies, contacts, and
opportunities through a pipeline (Wishlist → Applied → Phone Screen →
Interview → Offer → Rejected). Includes an AI-powered job search that finds
real, recent job postings via [Claude](https://www.anthropic.com/claude) and
adds them straight into your pipeline.

## Features

- **Companies, Contacts, Opportunities** — full CRUD with cascading deletes
  (deleting a company removes its contacts and opportunities).
- **AI job search** — searches the web for open roles matching a query
  (restricted to postings from the last week), and creates the matching
  Company + Opportunity records, skipping ones already in your database.
- **Search & filter** — client-side search across all three tables, plus a
  stage filter for opportunities.
- **Inline editing** — edit any record directly in the table.
- Input validation, type/length/format checks, and clear JSON error
  responses on every write endpoint.

## Tech stack

- **Backend**: Flask, SQLAlchemy, Flask-Migrate (Alembic), MySQL
- **Frontend**: React (Create React App), Bootstrap
- **AI**: [Anthropic API](https://platform.claude.com) (`claude-opus-4-8`)
  with the web search tool

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL running locally
- An [Anthropic API key](https://console.anthropic.com/settings/keys) (only
  needed for the AI job search feature)

### Backend

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost/crm_db
ANTHROPIC_API_KEY=sk-ant-...
```

Create the database and apply migrations:

```bash
mysql -u root -p -e "CREATE DATABASE crm_db;"
flask db upgrade
```

Run the API (serves on `http://127.0.0.1:5000`):

```bash
flask run
```

### Frontend

```bash
cd crm-frontend
npm install
npm start
```

Opens on `http://localhost:3000` and talks to the backend at
`http://127.0.0.1:5000`.

## API overview

| Method | Route | Description |
|---|---|---|
| GET/POST | `/companies` | List / create companies |
| GET/PUT/DELETE | `/companies/<id>` | Get, update, or delete a company |
| GET | `/companies/<id>/contacts` | Contacts for a company |
| GET | `/companies/<id>/opportunities` | Opportunities for a company |
| GET/POST | `/contacts` | List (optional `?company_id=`) / create contacts |
| GET/PUT/DELETE | `/contacts/<id>` | Get, update, or delete a contact |
| GET/POST | `/opportunities` | List (optional `?stage=`, `?company_id=`) / create opportunities |
| GET/PUT/DELETE | `/opportunities/<id>` | Get, update, or delete an opportunity |
| POST | `/opportunities/ai-search` | AI web search for job postings; body `{"query": "...", "limit": 5}` |

## Project structure

```
app.py              Flask app and routes
models.py            SQLAlchemy models (Company, Contact, Opportunity)
extensions.py         SQLAlchemy instance
ai_job_search.py       Claude-powered job search + DB insertion
migrations/           Alembic migrations
crm-frontend/          React app
```
