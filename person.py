import enum
import uuid
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Congregacoes(enum.Enum):
    SEDE = "Sede"
    CRISTO_REDENTOR = "Cristo Redentor"

class Conjuntos(enum.Enum):
    JOVENS = "Jovens"
    SENHORAS = "Senhoras"
    SENHORES = "Senhores"

class Pessoa(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    congregacao = db.Column(db.Enum(Congregacoes), nullable=False)
    conjunto = db.Column(db.Enum(Conjuntos), nullable=True)
    foto = db.Column(db.LargeBinary, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)

    def __init__(self, nome, cpf, data_nascimento, congregacao, conjunto=None, foto=None):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.congregacao = congregacao
        self.conjunto = conjunto
        self.foto = foto

    def json(self):
        return {
            'id': str(self.id),
            'nome': self.nome,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.isoformat(),
            'congregacao': self.congregacao.value,
            'conjunto': self.conjunto.value if self.conjunto else None,
            'tem_foto': self.foto is not None
        }
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def checkpassword(self, password):
        return check_password_hash(self.password_hash, password)