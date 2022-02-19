# services/users/project/api/models.py


from sqlalchemy.sql import func

from project import db


class User(db.Model):

    __tablename__ = "users_accounts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auth_key = db.Column(db.String(250), nullable=False)
    mac = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, username, email,mac,auth_token):
        self.username = username
        self.email = email
        self.mac = mac
        self.auth_key = auth_token

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'auth_key': self.username,
            'mac': self.username,
            'email': self.email,
            'active': self.active
        }
