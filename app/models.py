from app.app import db

# Recuperer les donnees de la base de donnees pour les afficher dans les templates

class ReferentielFonds(db.Model):
    __tablename__ = 'referentielfonds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ReferentielInstruments(db.Model):
    __tablename__ = 'referentielinstruments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))

class Positions(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('referentielfonds.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('referentielinstruments.id'), nullable=False)
    weight = db.Column(db.Numeric(5, 2))

    fund = db.relationship('ReferentielFonds', backref=db.backref('positions', lazy=True))
    instrument = db.relationship('ReferentielInstruments', backref=db.backref('positions', lazy=True))