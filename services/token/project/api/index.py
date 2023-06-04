# services/users/project/api/users.py


from flask import Blueprint, request, render_template,make_response,jsonify
from flask_restful import Resource, Api, reqparse
import random
from project import db
from project.api.models import User,Device,Business
from sqlalchemy import exc,extract
from project.api.huami_token import HuamiAmazfit
from sqlalchemy.sql.functions import func
from datetime import datetime
from firebase_admin import firestore
from collections import defaultdict

users_blueprint = Blueprint("index", __name__,template_folder='./template')
api = Api(users_blueprint)


class UsersPing(Resource):
    def get(self):
        return {"status": "success", "message": "pong!"}

class InitHuami(Resource):
    def post(self):
        post_data = request.get_json()
        if not post_data:
            return response_object, 400

        m = post_data.get('method')
        e = post_data.get('email')
        p = post_data.get('password')

        device = HuamiAmazfit(method=m,
                          email=e,
                          password=p)
    
        #return {"status": "success", "url": device.get_access_token()}
        device.login()

class HuamiCallback(Resource):
    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        method = request.form.get('url_callback')

        device = HuamiAmazfit(method="amazfit",
                          email=email,
                          password=password)

        device.get_access_token()
        device.login()

        device_keys = device.get_wearable_auth_keys()
        for device_key in device_keys:
            device_keys[device_key]

        #return device_keys
        return make_response(render_template('xiaomi.html',result = device_keys),200)

class HuamiCallbackApi(Resource):
    def post(self):
        post_data = request.get_json()
        email = post_data.get('email')
        password = post_data.get('password')
        response_object = {
            'status': 'fail',
            'message': 'Email o Password No coincide.'
        }
        device = HuamiAmazfit(method="amazfit",
                              email=email,
                              password=password)

        token_request = device.get_access_token()
        if token_request != "":
            device.login()
            device_keys = device.get_wearable_auth_keys()
            return device_keys
        else:
            return response_object

class HuamiCallbackApiRegister(Resource):
    def post(self):
        post_data = request.get_json()

        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400

        username= post_data.get('username')
        email= post_data.get('email')
        mac= post_data.get('mac')
        auth_key= post_data.get('auth_key')

        user = User.query.filter_by(email=email).first()

        if not user:
            db.session.add(User(
                username= username,
                email= email,
                mac= mac,
                auth_token= auth_key))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{email} was added!'
            return response_object, 201

class DeviceCallbackApi(Resource):
    def post(self):
        post_data = request.get_json()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400

        auth_token = post_data.get('auth_token')
        mac = post_data.get('mac')

        try:
            device = Device.query.filter_by(mac=mac).first()
            if not device:
                db.session.add(Device(mac=mac, auth_token=auth_token))
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{mac} was added!'
                return response_object, 201
            else:
                response_object['message'] = 'Device existe.'
                return response_object, 400
        except exc.IntegrityError:
            db.session.rollback()
            return response_object, 400

    def get(self,**parm):
        if parm :
            if parm["address"]:
                device = Device.query.filter_by(mac=parm["address"]).first()
                if device :
                    user_json = {}
                    user = User.query.filter_by(device_id=device.id).first()
                    if user:
                        user_json = user.to_json()
                    response_object = {
                        'status': 'success',
                        'device': device.to_json(),
                        'user' : user_json
                    }
                    return response_object, 200
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Dispositivo no existe : '+ parm["address"]
                    }
                    return response_object, 400
            else:    
                """Obtener device by ID"""
                device = Device.query.filter_by(id=parm["id"]).first()
                if device :
                    response_object = {
                        'status': 'success',
                        'business': device.to_json()
                    }
                    return response_object, 200
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Dispositivo no existe'  
                    }
                    return response_object, 400

        """Obtener todos los dispositivos"""
        response_object = {
            'status': 'success',
            'data': {
                'devices': [device.to_json() for device in Device.query.all()]
            }
        }
        return response_object, 200
    
    def put(slef):
        return {
            'status': 'success',
            'message': 'edit device'
        }

class UserCallbackApi(Resource):
    def post(self):
        post_data = request.get_json()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400

        username = post_data.get('username')
        email = post_data.get('email')
        password = post_data.get('password')
        name = post_data.get('name')
        auth_token = post_data.get('auth_token')
        
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                db.session.add(User(
                    username=username, 
                    email=email, 
                    password=password,
                    name=name,
                    auth_token=auth_token)
                )
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{email} was added!'
                return response_object, 201
            else:
                response_object['message'] = 'Sorry. Email already exists.'
                return response_object, 400
        except (exc.IntegrityError, ValueError):
            db.session.rollback()
            return response_object, 400

    def get(self,**parms):
        if parms:
            """Obtener usuario por id de empresa"""
            users = User.query.filter_by(business_id=parms["id_business"]).all()
            if users :
                response_object = {
                    'status': 'success',
                    'data': {
                        'users': [user.to_json() for user in users]
                    }
                }
                return response_object, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Empresa no tiene dispositivos vinculados'  
                }
                return response_object, 400
        """Obtener todos los usuarios"""
        response_object = {
            'status': 'success',
            'data': {
                'users': [user.to_json() for user in User.query.all()]
            }
        }
        return response_object, 200

class BusinessCallbackApi(Resource):
    def post(self):
        post_data = request.get_json()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400

        code_pairing = post_data.get('code_pairing')
        name = post_data.get('name')
        type_deploy = post_data.get('type_deploy')
        date_expire = post_data.get('expire_date')
        created_date = post_data.get('created_date') 
        id_campus = post_data.get('id_campus')
        id_group = post_data.get('id_group')
        
        try:
            business = Business.query.filter_by(code_pairing=code_pairing).first()
            if business:
                ## update bussines
                business.name = name
                business.type_deploy = type_deploy
                business.date_expire = date_expire
                business.created_date = created_date
                business.id_campus = id_campus
                business.id_group = id_group
                db.session.commit()

                response_object['status'] = 'success'
                response_object['message'] = f'{name} was updated!'
                return response_object, 200
            else:
                ## add new bussiness
                db.session.add(Business(
                    code_pairing=code_pairing, 
                    name=name, 
                    type_deploy=type_deploy,
                    date_expire=date_expire,
                    id_campus=id_campus,
                    created_date = created_date
                    id_group=id_group)
                )
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{name} was added!'
                return response_object, 201

        except (exc.IntegrityError, ValueError):
            db.session.rollback()
            return response_object, 400

    def get(self,**params):
        if request.path == '/api/business/pin/generate':
            unique_pin = self.generate_unique_pin()
            response_object = {
            'success': True,
            'message': 'Code pairing generate Ok.',
            'code_unique': unique_pin
            }
            return response_object,200
        
        endpoint = request.url_rule.endpoint
        if endpoint == 'index.bussines':
                """Obtener busines by ID"""
                business = Business.query.filter_by(id=params["id"]).first()
                if business :
                    response_object = {
                        'status': 'success',
                        'business': business.to_json()
                    }
                    return response_object, 200
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Dispositivo no existe'  
                    }
                    return response_object, 400
        
        elif endpoint == 'index.code':
                """Obtener busines by ID"""
                business = Business.query.filter_by(code_pairing=params["code"]).first()
                if business :
                    response_object = {
                        'status': 'success',
                        'business': business.to_json()
                    }
                    return response_object, 200
                else:
                    response_object = {
                        'status': 'fail',
                        'message': 'Dispositivo no existe'  
                    }
                    return response_object, 400
        

        """GET default  Obtener todas las empresas"""
        response_object = {
                'status': 'success',
                'data': {
                    'business': [business.to_json() for business in Business.query.filter(Business.id_group == 0, Business.id_campus == 0).all()]
                }
            }
        return response_object, 200
    
    def generate_unique_pin(self):
        while True:
            pin = str(random.randint(1000, 9999))
            existing_pin = Business.query.filter_by(code_pairing=pin).first()
            if existing_pin is None:
                return pin

class UserPairingCallbackApi(Resource):
    def post(self):
        post_data = request.get_json()
        response_object = {
            'success': False,
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400

        email = post_data.get('email')
        password = post_data.get('password')

        auth_token = post_data.get('auth_token')
        mac = post_data.get('mac')
        code_pairing = post_data.get('code_pairing')
        name_user = post_data.get('name_user')
        
        if not email:
            email = name_user

        try:
         
            user = User.query.filter_by(email=email).first()
            device = Device.query.filter_by(mac=mac).first()
            business = Business.query.filter_by(code_pairing=code_pairing).first()
            
            if not device:
                device = Device(auth_token=auth_token,mac=mac)

            if not user:
                user = User(
                    username=email.split("@")[0],
                    email=email,
                    password=password,
                    name=name_user,
                    auth_token=auth_token)
            if not business:
                response_object['success'] = False
                response_object['message'] = f'{code_pairing}, pairing code is not related to any company!'
                return response_object, 200


            user.device = device #One relation
            user.business = business #One relation
            db.session.add(user)
            db.session.commit()
            response_object['success'] = True
            response_object['message'] = f'{mac} device pairing 'f'{user.email} success!'
            return response_object, 201

        except (exc.IntegrityError, ValueError):
            db.session.rollback()
            return response_object, 400
# Reporting total devices createds by date
class ReportingByDate(Resource):
    def get(self):    
        try:
            devices = db.session.query(
                    extract('year', Device.created_date).label('year'),
                    extract('month', Device.created_date).label('month'),
                    db.func.count('*').label('devices')
                ).group_by('year', 'month').all()

            results = []
            for row in devices:
                if row.year != 0 and row.month != 0:
                    results.append({'month': datetime(row.year, row.month, 1).strftime('%B %Y'), 'devices': row.devices})
            response_object = {
                'status': 'success',
                 'data': {
                        'devices': results
                    }
                }
            return response_object,200
        except(exc.IntegrityError, ValueError):
            response_object = {
                    'status': 'fail',
                    'message': 'Error: '+ValueError  
                }
        return response_object,200

class ReportingGenerate(Resource):
    def get(self):
        fire_db = firestore.client()
        doc_ref = fire_db.collection('groupDevices').document('4a5395a9ed932202')
        doc_snapshot = doc_ref.get()
        # Obtener los datos del DocumentSnapshot
        data = doc_snapshot.to_dict()
        # Convertir los datos a JSON y enviar la respuesta
                
        return data["devices"],200

api.add_resource(HuamiCallback, '/xiaomi/callback') #web login
#Api login
api.add_resource(HuamiCallbackApi, '/api/auth/xiaomi/')
api.add_resource(HuamiCallbackApiRegister, '/api/auth/xiaomi/register')
# device API
api.add_resource(DeviceCallbackApi, '/api/device')
api.add_resource(DeviceCallbackApi, '/api/device/<id>', endpoint='device')
api.add_resource(DeviceCallbackApi, '/api/v1/check/address/<address>',endpoint='address')
#api.add_resource(HuamiCallbackApiRegister, '/api/device/delete')
# business API
api.add_resource(BusinessCallbackApi, '/api/business')
api.add_resource(BusinessCallbackApi, '/api/business/<id>',endpoint='bussines')
api.add_resource(BusinessCallbackApi, '/api/business/pin/<code>',endpoint='code')
api.add_resource(BusinessCallbackApi, '/api/business/pin/generate',endpoint='generate')

# user API
api.add_resource(UserCallbackApi, '/api/user')
api.add_resource(UserPairingCallbackApi, '/api/user/pairing')
api.add_resource(UserCallbackApi, '/api/user/bussines/<id_business>', endpoint='bussiness')
# reporting web:
api.add_resource(ReportingByDate, '/reporting/devices/activates')

# reporting devices xls
api.add_resource(ReportingGenerate,'/report/status/device')

 

@users_blueprint.route('/xiaomi/activate', methods=['GET'])
def index():
    return render_template('index.html')
