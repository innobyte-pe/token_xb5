# services/users/project/api/models.py


from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from project import db

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auth_token = db.Column(db.String(250), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

    device_id = db.Column(db.Integer,db.ForeignKey('device.id'))
    device = db.relationship("Device",backref="user")

    business_id = db.Column(db.Integer,db.ForeignKey('business.id'),nullable=True)
    business = db.relationship("Business",backref="user")

    def __init__(self, auth_token,name,username,password,email):
        self.auth_token = auth_token
        self.name = name
        self.username = username
        self.password =password
        self.email = email


    def to_json(self):
        device_json = self.device
        business_json = self.business
        if self.device == None:
            device_json = False
        else:
            device_json = self.device.to_json()
        
        if self.business == None:
            business_json = False
        else:
            business_json = self.business.to_json()

        
        return {
            'id': self.id,
            'token': self.auth_token,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'active': self.active,
            'created_date': str(self.created_date),
            'device': device_json,
            'business': business_json
        }

class Device(db.Model):

    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auth_key = db.Column(db.String(250), nullable=False)
    mac = db.Column(db.String(128), nullable=False)
    number = db.Column(db.String(128), nullable=True)
    serial = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    def __init__(self,mac,auth_token):
        self.mac = mac
        self.auth_key = auth_token

    def to_json(self):
        return {
            'id': self.id,
            'auth_key': self.auth_key,
            'mac': self.mac,
            'number': self.number,
            'serial': self.serial,
            'created_date': str(self.created_date),
            'active': self.active
        }

class Business(db.Model):

    __tablename__ = "business"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_pairing = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    type_deploy = db.Column(db.String(20), nullable=False)
    date_expire = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    
    #id_campus = db.Column(db.Integer, db.ForeignKey('business.id'))
    #campus = db.relationship('Business', backref=db.backref('parent', remote_side=[id]))

    id_campus = db.Column(db.Integer, db.ForeignKey('business.id'))
    campus = db.relationship('Business', foreign_keys=[id_campus], backref=db.backref('parent', remote_side=[id]))

    id_group = db.Column(db.Integer, db.ForeignKey('business.id'))
    group = db.relationship('Business', foreign_keys=[id_group], backref=db.backref('parent_group', remote_side=[id]))
     

    def __init__(self, code_pairing, name, type_deploy, date_expire, id_campus,id_group):
        self.code_pairing = code_pairing
        self.name = name
        self.type_deploy = type_deploy
        self.date_expire = date_expire
        self.id_campus = id_campus
        self.id_group = id_group

    def to_json(self):
        serialized = {
            'id': self.id,
            'code_pairing': self.code_pairing,
            'name': self.name,
            'type_deploy': self.type_deploy,
            'date_expire': str(self.date_expire),
            'created_date': str(self.created_date),
            'active': self.active,
            'campus': [],
            'groups': [],
        }
        if self.campus:
           serialized['campus'] = [campus.to_json() for campus in self.campus]

        if self.group:
           serialized['groups'] = [group.to_json() for group in self.group]
        return serialized
