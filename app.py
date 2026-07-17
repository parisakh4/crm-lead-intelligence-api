from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from models import Company, Contact, Opportunity
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from extensions import db
db.init_app(app)
migrate = Migrate(app, db)
app.extensions['migrate'].db = db

MAX_NAME_LEN = 100
MAX_EMAIL_LEN = 100
MAX_PHONE_LEN = 20
MAX_INDUSTRY_LEN = 100
MAX_LOCATION_LEN = 100
STAGES = ["Wishlist", "Applied", "Phone Screen", "Interview", "Offer", "Rejected"]


# -- Validation helpers -------------------------------------------------
# Each helper returns (present, value, error):
#   present: whether the field key was in the payload at all (PUT routes
#            use this to decide whether to touch the existing value)
#   value:   the cleaned value, or None if absent/blank/null
#   error:   a message if the supplied value was invalid, else None
# Blank strings and JSON null both normalize to value=None so optional
# fields sent by the frontend as "" don't trip validation.

def clean_str(data, field, max_length=None):
    if field not in data:
        return False, None, None
    value = data.get(field)
    if value is None:
        return True, None, None
    if not isinstance(value, str):
        return True, None, f"{field} must be a string"
    value = value.strip()
    if not value:
        return True, None, None
    if max_length and len(value) > max_length:
        return True, None, f"{field} must be {max_length} characters or fewer"
    return True, value, None


def clean_email(data, field='email'):
    present, value, error = clean_str(data, field, max_length=MAX_EMAIL_LEN)
    if error or value is None:
        return present, value, error
    if '@' not in value:
        return present, None, f"{field} must be a valid email address"
    return present, value, None


def clean_stage(data, field='stage'):
    present, value, error = clean_str(data, field)
    if error or value is None:
        return present, value, error
    if value not in STAGES:
        return present, None, f"{field} must be one of: {', '.join(STAGES)}"
    return present, value, None


def clean_int(data, field):
    if field not in data:
        return False, None, None
    value = data.get(field)
    if value is None:
        return True, None, None
    if isinstance(value, bool) or not isinstance(value, int):
        return True, None, f"{field} must be an integer"
    return True, value, None


def clean_number(data, field):
    if field not in data:
        return False, None, None
    value = data.get(field)
    if value is None:
        return True, None, None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return True, None, f"{field} must be a number"
    return True, float(value), None


def get_json_body():
    """Parsed JSON dict, or None if the body is missing/malformed/not an object."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@app.route('/')
def home():
    return "App with db is running!"


# API endpoint to create a new company
@app.route('/companies', methods=['POST'])
def add_company():
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    _, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif not name:
        errors.append("name is required")
    _, industry, err = clean_str(data, 'industry', max_length=MAX_INDUSTRY_LEN)
    if err:
        errors.append(err)
    _, location, err = clean_str(data, 'location', max_length=MAX_LOCATION_LEN)
    if err:
        errors.append(err)
    _, email, err = clean_email(data)
    if err:
        errors.append(err)

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    company = Company(name=name, industry=industry, location=location, email=email)

    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company created"}), 201


# API endpoint to get all companies
@app.route('/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()

    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "location": c.location,
            "email": c.email
        })

    return jsonify(result)


# API endpoint to get a specific company by ID
@app.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)

    return jsonify({
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "location": company.location,
        "email": company.email
    })

# API endpoint to update a company
@app.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    company = Company.query.get_or_404(company_id)
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    name_present, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif name_present and name is None:
        errors.append("name cannot be empty")
    industry_present, industry, err = clean_str(data, 'industry', max_length=MAX_INDUSTRY_LEN)
    if err:
        errors.append(err)
    location_present, location, err = clean_str(data, 'location', max_length=MAX_LOCATION_LEN)
    if err:
        errors.append(err)
    email_present, email, err = clean_email(data)
    if err:
        errors.append(err)

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    if name_present:
        company.name = name
    if industry_present:
        company.industry = industry
    if location_present:
        company.location = location
    if email_present:
        company.email = email

    db.session.commit()

    return jsonify({"message": "Company updated"})

# API endpoint to delete a company
@app.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)

    db.session.delete(company)
    db.session.commit()

    return jsonify({"message": "Company deleted"})

# API endpoint to post a new contact
@app.route('/contacts', methods=['POST'])
def add_contact():
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    _, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif not name:
        errors.append("name is required")
    _, email, err = clean_email(data)
    if err:
        errors.append(err)
    _, phone, err = clean_str(data, 'phone', max_length=MAX_PHONE_LEN)
    if err:
        errors.append(err)
    _, company_id, err = clean_int(data, 'company_id')
    if err:
        errors.append(err)
    elif company_id is None:
        errors.append("company_id is required")
    elif not Company.query.get(company_id):
        errors.append("Company not found")

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    contact = Contact(
        name=name,
        email=email,
        phone=phone,
        company_id=company_id
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({"message": "Contact created"}), 201

# API endpoint to get all contacts
@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.all()

    result = []
    for c in contacts:
        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "company_id": c.company_id
        })

    return jsonify(result)

# API endpoint to get a specific contact by ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    return jsonify({
        "id": contact.id,
        "name": contact.name,
        "email": contact.email,
        "phone": contact.phone,
        "company_id": contact.company_id
    })

# API endpoint to update a contact
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    name_present, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif name_present and name is None:
        errors.append("name cannot be empty")
    email_present, email, err = clean_email(data)
    if err:
        errors.append(err)
    phone_present, phone, err = clean_str(data, 'phone', max_length=MAX_PHONE_LEN)
    if err:
        errors.append(err)
    company_id_present, company_id, err = clean_int(data, 'company_id')
    if err:
        errors.append(err)
    elif company_id_present:
        if company_id is None:
            errors.append("company_id cannot be empty")
        elif not Company.query.get(company_id):
            errors.append("Company not found")

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    if name_present:
        contact.name = name
    if email_present:
        contact.email = email
    if phone_present:
        contact.phone = phone
    if company_id_present:
        contact.company_id = company_id

    db.session.commit()

    return jsonify({"message": "Contact updated"})

# API endpoint to delete a contact
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message": "Contact deleted"})

# API endpoint to get contacts from a specific company
@app.route('/companies/<int:company_id>/contacts', methods=['GET'])
def get_company_contacts(company_id):
    company = Company.query.get_or_404(company_id)
    contacts = company.contacts

    result = []
    for c in contacts:
        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "company_id": c.company_id
        })

    return jsonify(result)


# API endpoint to post a new opportunity
@app.route('/opportunities', methods=['POST'])
def add_opportunity():
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    _, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif not name:
        errors.append("name is required")
    _, stage, err = clean_stage(data)
    if err:
        errors.append(err)
    elif not stage:
        errors.append("stage is required")
    _, value, err = clean_number(data, 'value')
    if err:
        errors.append(err)
    _, company_id, err = clean_int(data, 'company_id')
    if err:
        errors.append(err)
    elif company_id is None:
        errors.append("company_id is required")
    elif not Company.query.get(company_id):
        errors.append("Company not found")

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    opportunity = Opportunity(
        name=name,
        value=value,
        stage=stage,
        company_id=company_id
    )

    db.session.add(opportunity)
    db.session.commit()

    return jsonify({"message": "Opportunity created"}), 201


# API endpoint to get all opportunities
@app.route('/opportunities', methods=['GET'])
def get_opportunities():
    opportunities = Opportunity.query.all()

    result = []
    for o in opportunities:
        result.append({
            "id": o.id,
            "name": o.name,
            "value": o.value,
            "stage": o.stage,
            "company_id": o.company_id
        })

    return jsonify(result)

# API endpoint to get a specific opportunity by ID
@app.route('/opportunities/<int:opportunity_id>', methods=['GET'])
def get_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)

    return jsonify({
        "id": opportunity.id,
        "name": opportunity.name,
        "value": opportunity.value,
        "stage": opportunity.stage,
        "company_id": opportunity.company_id
    })

# API endpoint to get opportunities from a specific company
@app.route('/companies/<int:company_id>/opportunities', methods=['GET'])
def get_company_opportunities(company_id):
    company = Company.query.get_or_404(company_id)
    opportunities = company.opportunities

    result = []
    for o in opportunities:
        result.append({
            "id": o.id,
            "name": o.name,
            "value": o.value,
            "stage": o.stage,
            "company_id": o.company_id
        })

    return jsonify(result)


# API endpoint to update an opportunity
@app.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
def update_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    data = get_json_body()
    if data is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    errors = []
    name_present, name, err = clean_str(data, 'name', max_length=MAX_NAME_LEN)
    if err:
        errors.append(err)
    elif name_present and name is None:
        errors.append("name cannot be empty")
    stage_present, stage, err = clean_stage(data)
    if err:
        errors.append(err)
    elif stage_present and stage is None:
        errors.append("stage cannot be empty")
    value_present, value, err = clean_number(data, 'value')
    if err:
        errors.append(err)
    company_id_present, company_id, err = clean_int(data, 'company_id')
    if err:
        errors.append(err)
    elif company_id_present:
        if company_id is None:
            errors.append("company_id cannot be empty")
        elif not Company.query.get(company_id):
            errors.append("Company not found")

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    if name_present:
        opportunity.name = name
    if stage_present:
        opportunity.stage = stage
    if value_present:
        opportunity.value = value
    if company_id_present:
        opportunity.company_id = company_id

    db.session.commit()

    return jsonify({"message": "Opportunity updated"})

# API endpoint to delete an opportunity
@app.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)

    db.session.delete(opportunity)
    db.session.commit()

    return jsonify({"message": "Opportunity deleted"})


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({"error": e.description}), e.code


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
