from flask import Blueprint, request
from admin import Admin
from database import db
from flask_jwt_extended import jwt_required


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin', methods=['POST'])
@jwt_required()
def post_admin():
    """
    Cria admin
    ---
    tags:
      - Admin
    parameters:
      - in: body
        name: admin
        description: Objeto JSON representando o admin a ser criado
        required: true
        schema:
          type: object
          properties:
            pessoa_id:
              type: string
    """
    dados = request.get_json()
    pessoa_id = dados.get('pessoa_id')

    if not pessoa_id:
        return {"msg": "pessoa_id é obrigatório"}, 400

    novo_admin = Admin(pessoa_id=pessoa_id)
    db.session.add(novo_admin)
    db.session.commit()

    return {"msg": "Admin criado com sucesso", "admin": novo_admin.json()}, 201

@admin_bp.route('/api/admin/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_admin(id):
    """
    Deleta admin
    ---
    tags:
      - Admin
    parameters:
      - in: path
        name: id
        description: ID do admin a ser deletado
        required: true
        type: string
    """
    admin = Admin.query.get(id)

    if not admin:
        return {"msg": "Admin não encontrado"}, 404

    db.session.delete(admin)
    db.session.commit()

    return {"msg": "Admin deletado com sucesso"}, 200