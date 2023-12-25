from apps import db
from sqlalchemy.orm import backref

# we can use one table, and then display active connections by filtering the "status" column.

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




class operationResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_identifier = db.Column(db.String(6), db.ForeignKey('all_agents.identifier', ondelete='CASCADE'))
    parent = db.relationship('allAgents', backref=backref('children', passive_deletes=True))
    operationTested = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    details = db.Column(db.String(100), nullable=False)

