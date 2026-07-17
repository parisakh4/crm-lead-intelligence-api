from extensions import db

# Define a model for the Company table
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    email = db.Column(db.String(100))


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship(
        'Company',
        backref=db.backref('contacts', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    )


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    value = db.Column(db.Float)
    stage = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship(
        'Company',
        backref=db.backref('opportunities', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    )