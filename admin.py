import uuid
from database import db

class Admin(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pessoa_id = db.Column(db.String(36), db.ForeignKey('pessoa.id'), nullable=False)

    def __init__(self, pessoa_id):
        self.pessoa_id = pessoa_id

    def json(self):
        return {
            'id': str(self.id),
            'pessoa_id': self.pessoa_id
        }