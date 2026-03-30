from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
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


@app.route('/')
def home():
    return "App with db is running!"


# API endpoint to create a new company
@app.route('/companies', methods=['POST'])
def add_company():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({"error": "Company name is required"}), 400

    company = Company(
        name=data.get('name'),
        industry=data.get('industry'),
        location=data.get('location'),
        email=data.get('email')
    )

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
    data = request.get_json()

    company.name = data.get('name', company.name)
    company.industry = data.get('industry', company.industry)
    company.location = data.get('location', company.location)
    company.email = data.get('email', company.email)

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
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({"error": "Contact name is required"}), 400
    if not data.get('company_id'):
        return jsonify({"error": "company_id is required"}), 400

    contact = Contact(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        company_id=data.get('company_id')
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
    data = request.get_json()

    contact.name = data.get('name', contact.name)
    contact.email = data.get('email', contact.email)
    contact.phone = data.get('phone', contact.phone)
    contact.company_id = data.get('company_id', contact.company_id)

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
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({"error": "Opportunity name is required"}), 400
    if not data.get('stage'):
        return jsonify({"error": "stage is required"}), 400
    if not data.get('company_id'):
        return jsonify({"error": "company_id is required"}), 400

    opportunity = Opportunity(
        name=data.get('name'),
        value=data.get('value'),
        stage=data.get('stage'),
        company_id=data.get('company_id')
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
    data = request.get_json()

    opportunity.name = data.get('name', opportunity.name)
    opportunity.value = data.get('value', opportunity.value)
    opportunity.stage = data.get('stage', opportunity.stage)
    opportunity.company_id = data.get('company_id', opportunity.company_id)

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


# Run the app
if __name__ == '__main__':
    app.run(debug=True)