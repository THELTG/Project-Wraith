from apps import db
from sqlalchemy.sql import func

# we can use one table, and then display active connections by filtering the "status" column.

class allAgents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(200), unique=True, nullable=False)
    ipAddress = db.Column(db.String(50), nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20))
    lastCheckin = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    integrity = db.Column(db.String(50), nullable=False)
    operatingSystem = db.Column(db.String(100), nullable=False)