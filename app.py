import os
from flask_migrate import Migrate
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from database import db
from routes.person import person_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

jwt = JWTManager(app)

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(person_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

with app.app_context():
    db.create_all()
    
swagger = Swagger(app, template={
    "swagger": "2.0",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Bearer <JWT>"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
})

if __name__ == '__main__':
    app.run(debug=True)