from flask import jsonify, render_template, request
from app.app import app, db
from app.models import ReferentielFonds, ReferentielInstruments, Positions

# Retourner la liste des fonds avec un filtre de recherche
@app.route('/api/fonds', methods=['GET'])
def api_fonds():
    search_query = request.args.get('search', '')
    if search_query:
        results = ReferentielFonds.query.filter(ReferentielFonds.name.ilike(f'%{search_query}%')).all()
    else:
        results = ReferentielFonds.query.all()
    
    fonds = [{'id': fund.id, 'name': fund.name} for fund in results]
    return jsonify(fonds)

# Retourner la liste des instruments
@app.route('/api/instruments', methods=['GET'])
def api_instruments():
    instruments = ReferentielInstruments.query.all()
    return jsonify([{'id': instrument.id, 'name': instrument.name, 'type': instrument.type} for instrument in instruments])

# Retourner les positions d'un fond
@app.route('/api/positions/<int:fund_id>', methods=['GET'])
def api_positions(fund_id):
    positions = Positions.query.filter_by(fund_id=fund_id).all()
    total_weight = sum(position.weight for position in positions)
    positions_data = [{
        'instrument': {
            'name': position.instrument.name,
            'type': position.instrument.type
        },
        'weight': float(position.weight)
    } for position in positions]
    return jsonify({
        'positions': positions_data,
        'total_weight': total_weight
    })

# Routes pour les pages web

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fonds')
def fonds():
    return render_template('view_funds.html')

@app.route('/instruments')
def instruments():
    return render_template('view_instruments.html')

@app.route('/positions/<int:fund_id>')
def positions(fund_id):
    return render_template('view_positions.html', fund_id=fund_id)