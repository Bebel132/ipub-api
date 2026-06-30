import os

from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from database import db

from person import Pessoa

card_bp = Blueprint('card', __name__)

@card_bp.route('/api/cards/<string:id>', methods=['GET'])
@jwt_required()
def get_card(id):
    """
    Retorna a carteirinha de uma pessoa específica.
    ---
    tags:
      - Carteirinhas
    produces:
      - image/png
    parameters:
      - in: path
        name: id
        description: ID da pessoa a ser retornada
        required: true
        type: string
    security:
      - Bearer: []
    responses:
      200:
        description: Carteirinha da pessoa
        schema:
          type: file
      404:
        description: Pessoa não encontrada
    """
    pessoa = db.session.get(Pessoa, id)
    if not pessoa:
        return jsonify({"error": "Pessoa não encontrada"}), 404
    
    image = generate_card(pessoa)

    return send_file(
        image,
        mimetype="image/png",
        download_name="carteirinha.png"
    )

CARD_LAYOUT = {
    "photo": (115, 200),
    "location": (1430, 65),
    "name": (1360, 130),
    "congregation": (1100, 320),
    "group": (1450, 320),
    "validity_year": (1275, 485),
    "validity_month": (1215, 485),
    "validity_day": (1145, 485),
    "cpf": (1480, 485),
    "shepherd": (1060, 255)
}

def generate_card(person):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    template = Image.open(os.path.join(BASE_DIR, "carteirinha_template.png"))
    draw = ImageDraw.Draw(template)

    font = ImageFont.truetype(os.path.join(BASE_DIR, "font", "Inter-VariableFont_opsz,wght.ttf"), 24)

    if person.foto:
        foto = Image.open(BytesIO(person.foto)).convert("RGB")
        foto = foto.resize((250, 250))
        template.paste(foto, CARD_LAYOUT["photo"])

    draw.text(CARD_LAYOUT["location"], "Fortaleza", fill="black", font=font)
    draw.text(CARD_LAYOUT["name"], str(person.nome), fill="black", font=font)
    draw.text(CARD_LAYOUT["congregation"], str(person.congregacao.value) if person.congregacao else "N/A", fill="black", font=font)
    draw.text(CARD_LAYOUT["group"], str(person.conjunto.value) if person.conjunto else "N/A", fill="black", font=font)
    draw.text(CARD_LAYOUT["validity_year"], "2030", fill="black", font=font)
    draw.text(CARD_LAYOUT["validity_month"], "01", fill="black", font=font)
    draw.text(CARD_LAYOUT["validity_day"], "30", fill="black", font=font)
    draw.text(CARD_LAYOUT["cpf"], str(person.cpf), fill="black", font=font)
    draw.text(CARD_LAYOUT["shepherd"], "Jonias da Silva Castro", fill="black", font=font)

    output = BytesIO()
    template.save(output, format="PNG")
    output.seek(0)

    return output