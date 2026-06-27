from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from decorators import admin_or_owner, admin_required
from person import Pessoa, Congregacoes, Conjuntos
from database import db
from datetime import datetime

person_bp = Blueprint('person', __name__)

@person_bp.route('/api/pessoas', methods=['GET'])
@jwt_required()
def get_pessoas():
    """
    Retorna a lista de todas as pessoas cadastradas.
    ---
    tags:
      - Pessoas
    security:
      - Bearer: []
    responses:
      200:
        description: Uma lista de pessoas
    """
    result = [pessoa.json() for pessoa in Pessoa.query.all()]
    result.sort(key=lambda x: x['nome'])
    
    for pessoa in result:
        pessoa['idade'] = (datetime.now().year - datetime.strptime(pessoa['data_nascimento'], '%Y-%m-%d').year)-1
        pessoa['tem_foto'] = bool(pessoa['tem_foto'])

    return jsonify(result), 200

@person_bp.route('/api/pessoas', methods=['POST'])
@jwt_required()
@admin_required
def create_pessoa():
    """
    Cria uma nova pessoa.
    ---
    tags:
      - Pessoas
    parameters:
      - in: body
        name: pessoa
        description: Objeto JSON representando a pessoa a ser criada
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            cpf:
              type: string
            data_nascimento:
              type: string
              format: date
            congregacao:
              type: string
              enum: [Sede, Cristo Redentor]
            conjunto:
              type: string
              enum: [Jovens, Senhoras, Senhores]
            senha:
              type: string
    """
    dados = request.get_json()
    
    try:
        nova_pessoa = Pessoa(
            nome=dados['nome'],
            cpf=dados['cpf'],
            data_nascimento=datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date(),
            congregacao=Congregacoes(dados['congregacao']),
            conjunto=Conjuntos(dados['conjunto']) if dados.get('conjunto') else None
        )

        nova_pessoa.set_password(dados['senha'])
        
        db.session.add(nova_pessoa)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify(nova_pessoa.json()), 201

@person_bp.route('/api/pessoas/<string:id>', methods=['PUT'])
@jwt_required()
@admin_or_owner(param="id")
def update_pessoa(id):
    """
    Atualiza uma pessoa existente.
    ---
    tags:
      - Pessoas
    parameters:
      - in: path
        name: id
        description: ID da pessoa a ser atualizada
        required: true
        type: string
      - in: body
        name: pessoa
        description: Objeto JSON representando a pessoa a ser atualizada
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            cpf:
              type: string
            data_nascimento:
              type: string
              format: date
            congregacao:
              type: string
              enum: [Sede, Cristo Redentor]
            conjunto:
              type: string
              enum: [Jovens, Senhoras, Senhores]
    """
    pessoa = db.session.get(Pessoa, id)
    
    if not pessoa:
        return jsonify({"error": "Pessoa não encontrada"}), 404
    
    dados = request.get_json()
    
    try:
        pessoa.nome = dados['nome']
        pessoa.cpf = dados['cpf']
        pessoa.data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
        pessoa.congregacao = Congregacoes(dados['congregacao'])
        pessoa.conjunto = Conjuntos(dados['conjunto']) if dados.get('conjunto') else None

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return jsonify(pessoa.json()), 200

@person_bp.route('/api/pessoas/<string:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_pessoa(id):
    """
    Exclui uma pessoa existente.
    ---
    tags:
      - Pessoas
    parameters:
      - in: path
        name: id
        description: ID da pessoa a ser atualizada
        required: true
        type: string
    """
    pessoa = db.session.get(Pessoa, id)
    if not pessoa:
        return jsonify({"error": "Pessoa não encontrada"}), 404
    
    try:
        db.session.delete(pessoa)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return {}, 200

@person_bp.route('/api/pessoas/<string:id>/foto', methods=['POST'])
@jwt_required()
@admin_or_owner(param="id")
def upload_foto(id):
    """
    Faz upload da foto de uma pessoa existente.
    ---
    tags:
      - Pessoas
    parameters:
      - in: path
        name: id
        description: ID da pessoa a quem upload a foto
        required: true
        type: string
      - in: formData
        name: foto
        description: Arquivo da foto a ser enviado
        required: true
        type: file
    """
    pessoa = db.session.get(Pessoa, id)
    if not pessoa:
        return jsonify({"error": "Pessoa não encontrada"}), 404
    
    if 'foto' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    foto = request.files['foto']
    
    try:
        pessoa.foto = foto.read()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    return {}, 200

@person_bp.route('/api/pessoas/<string:id>/foto', methods=['GET'])
def get_foto(id):
    """
    Retorna a foto de uma pessoa existente.
    ---
    tags:
      - Pessoas
    parameters:
      - in: path
        name: id
        description: ID da pessoa a quem a foto pertence
        required: true
        type: string
    """
    pessoa = db.session.get(Pessoa, id)
    if not pessoa:
        return jsonify({"error": "Pessoa não encontrada"}), 404
    
    if not pessoa.foto:
        return jsonify({"error": "Pessoa não possui foto"}), 404
    
    return pessoa.foto, 200, {'Content-Type': 'image/jpeg'}