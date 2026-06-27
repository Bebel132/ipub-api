from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies
from database import db
from admin import Admin
from person import Pessoa


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """
    Endpoint de login para autenticação de usuários.
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: credentials
        description: Credenciais do usuário
        required: true
        schema:
          type: object
          properties:
            cpf:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token de acesso gerado com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Credenciais inválidas
    """
    cpf = request.json.get("cpf", None)
    password = request.json.get("password", None)

    user = Pessoa.query.filter_by(cpf=cpf).first()

    print(user, cpf)

    if not user or not user.checkpassword(password):
        return jsonify({"msg": "Bad cpf or password"}), 401
    
    is_admin = Admin.query.filter_by(pessoa_id=user.id).first() is not None

    access_token = create_access_token(identity=user.id, additional_claims={"is_admin": is_admin})
    return jsonify({
      "msg": "Login realizado",
      "access_token": access_token
    }), 200

@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    """
    Endpoint para obter informações do usuário autenticado.
    ---
    tags:
      - Autenticação
    security:
      - Bearer: []
    responses:
      200:
        description: Informações do usuário autenticado
        schema:
          type: object
          properties:
            id:
              type: integer
            nome:
              type: string
            cpf:
              type: string
    """
    user_id = get_jwt_identity()
    user = Pessoa.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "nome": user.nome,
        "cpf": user.cpf
    }), 200

    return get_user_info()