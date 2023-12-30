from apps import db
from sqlalchemy.orm import backref

class allAgents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(6), unique=True, nullable=False)
    ipAddress = db.Column(db.String(20), nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20))
    lastCheckin = db.Column(db.String(100))
    integrity = db.Column(db.String(50), nullable=False)
    operatingSystem = db.Column(db.String(100), nullable=False)

class operationDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operationName = db.Column(db.String(50), unique=True, nullable=False)
    genericDetail = db.Column(db.Text, nullable=False)
    detailTrue = db.Column(db.Text, nullable=True)
    detailFalse = db.Column(db.Text, nullable=True)

class operationResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_identifier = db.Column(db.String(6), db.ForeignKey('all_agents.identifier', ondelete='CASCADE')) # fk, delete on cascade
    operationTested = db.Column(db.String(50), db.ForeignKey('operation_details.operationName'), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    time = db.Column(db.Integer, nullable=False) # unix timestamp
    parent = db.relationship('allAgents', backref=backref('children', passive_deletes=True)) # creates a relationship between allAgents and operationResults
    # details = db.relationship('operationDetails', backref='operation_results', uselist=False)


