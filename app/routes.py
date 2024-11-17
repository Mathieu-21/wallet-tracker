from flask import jsonify, render_template, request, current_app
from app.app import app, db
from app.models import ReferentielFonds, ReferentielInstruments, Positions
import json
import os

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

# Supprimer une position
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

@app.route('/create_template')
def create_template():
    return render_template('create_template.html')

@app.route('/positions/<int:fund_id>')
def positions(fund_id):
    return render_template('view_positions.html', fund_id=fund_id)

@app.route('/reporting/create_reporting/get_blocks/', methods=['GET'])
def get_blocks():
    file_path = os.path.join(current_app.root_path, 'static', 'json', 'correspondance_templates_blocks.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            result = [
                {
                    'nom_block': block.get('nom_block', ''),
                    'description_block': block.get('description_block', ''),
                    'position_x_start': block.get('position_x_start', 0),
                    'position_y_start': block.get('position_y_start', 0),
                    'position_x_end': block.get('position_x_end', 0),
                    'position_y_end': block.get('position_y_end', 0)
                }
                for block in data
            ]
            return jsonify({'data': result})
    except FileNotFoundError:
        return jsonify({'error': 'JSON file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON data'}), 400
    
@app.route('/reporting/create_reporting/get_templates/', methods=['GET'])
def get_templates():
    file_path = os.path.join(current_app.root_path, 'static', 'json', 'ref_templates_reporting.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            result = [
                {
                    'nom_template': template.get('nom_template', ''),
                    'id_template': template.get('id_template', 0)
                }
                for template in data
            ]
            return jsonify({'data': result})
    except FileNotFoundError:
        return jsonify({'error': 'JSON file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON data'}), 400
    
@app.route('/reporting/create_reporting/get_blocks_template/', methods=['POST'])
def get_blocks_template():
    
    data = request.json
    id_template = data['id_template']

    file_path_blocks = os.path.join(current_app.root_path, 'static', 'json', 'correspondance_templates_blocks.json')
    file_path_blocks_reporting = os.path.join(current_app.root_path, 'static', 'json', 'ref_blocks_reporting.json')

    try:
        with open(file_path_blocks, 'r') as file_blocks, open(file_path_blocks_reporting, 'r') as file_blocks_reporting:
            blocks_data = json.load(file_blocks)
            blocks_reporting_data = json.load(file_blocks_reporting)

            filtered_blocks = [
                block for block in blocks_data if block.get('id_template') == id_template
            ]

            result = []
            for block in filtered_blocks:
                matching_block_reporting = next(
                    (br for br in blocks_reporting_data if br.get('id_block') == block.get('id_template_block')), {}
                )
                result.append({
                    'nom_block': matching_block_reporting.get('nom_block', ''),
                    'description_block': matching_block_reporting.get('description_block', ''),
                    'position_x_start': block.get('position_x_start', 0),
                    'position_y_start': block.get('position_y_start', 0),
                    'position_x_end': block.get('position_x_end', 0),
                    'position_y_end': block.get('position_y_end', 0),
                    'num_page': block.get('num_page', 0)
                })

            result = sorted(
                result,
                key=lambda x: (
                    x['position_y_start'],
                    x['position_x_start'],
                    x['position_y_end'],
                    x['position_x_end']
                )
            )
            
            return jsonify({'data': result})

    except FileNotFoundError:
        return jsonify({'error': 'JSON file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON data'}), 400

