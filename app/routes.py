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

# Ajouter un fond
@app.route('/api/fonds', methods=['POST'])
def add_fund():
    data = request.get_json()
    fund_name = data.get('name', '').strip()
    if fund_name:
        new_fund = ReferentielFonds(name=fund_name)
        db.session.add(new_fund)
        db.session.commit()
        return jsonify({'success': True}), 201
    else:
        return jsonify({'success': False, 'message': 'Il manque le nom du fond'}), 400


# Retourner la liste des instruments
@app.route('/api/instruments', methods=['GET'])
def api_instruments():
    instruments = ReferentielInstruments.query.all()
    return jsonify([{'id': instrument.id, 'name': instrument.name, 'type': instrument.type} for instrument in instruments])

# Ajouter un instrument
@app.route('/api/instruments', methods=['POST'])
def add_instrument():
    data = request.get_json()
    name = data.get('name', '').strip()
    type = data.get('type', '').strip()
    if name and type:
        new_instrument = ReferentielInstruments(name=name, type=type)
        db.session.add(new_instrument)
        db.session.commit()
        return jsonify({'success': True}), 201
    else:
        return jsonify({'success': False, 'message': 'Nom et type de l\'instrument requis'}), 400

# Retourner les positions d'un fond
@app.route('/api/positions/<int:fund_id>', methods=['GET'])
def api_positions(fund_id):
    positions = Positions.query.filter_by(fund_id=fund_id).all()
    total_weight = sum(position.weight for position in positions)
    positions_data = [{
        'id': position.id,
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

@app.route('/api/positions/<int:position_id>', methods=['DELETE'])
def delete_position(position_id):
    position = Positions.query.get(position_id)
    if position:
        db.session.delete(position)
        db.session.commit()
        return jsonify({'success': True})
    print('Position non trouvée')
    return jsonify({'success': False, 'message': 'Position non trouvée'}), 404

# Ajouter une position à un fond    
@app.route('/api/positions', methods=['POST'])
def add_position():
    data = request.get_json()
    fund_id = data.get('fund_id')
    instrument_id = data.get('instrument_id')
    weight = data.get('weight')
    current_positions = Positions.query.filter_by(fund_id=fund_id).all()
    total_weight = sum(position.weight for position in current_positions) + weight
    if total_weight > 100:
        return jsonify({'success': False, 'message': 'Poids total dépasse 100%'}), 400
    new_position = Positions(fund_id=fund_id, instrument_id=instrument_id, weight=weight)
    db.session.add(new_position)
    db.session.commit()
    return jsonify({'success': True}), 201
    
# Vérifier si la position est deja definie pour un fond
@app.route('/api/positions/<int:fund_id>/check', methods=['POST'])
def check_position(fund_id):
    data = request.get_json()
    instrument_id = data.get('instrument_id')
    exists = Positions.query.filter_by(fund_id=fund_id, instrument_id=instrument_id).first() is not None
    return jsonify({'exists': exists})

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