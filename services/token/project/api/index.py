# services/users/project/api/users.py


from flask import Blueprint, request, render_template
from flask_restful import Resource, Api

from project import db
from project.api.models import User,Device,Business
from sqlalchemy import exc
from project.api.huami_token import HuamiAmazfit

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

        return device_keys

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

    def get(self):
        """Obtener todos los usuarios"""
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

    def get(self):
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
        date_expire = post_data.get('date_expire')
        
        try:
            business = Business.query.filter_by(code_pairing=code_pairing).first()
            if business:
                response_object['message'] = 'Sorry. Code Pairing already exists.'
                return response_object, 400

            business = Business.query.filter_by(name=name).first()
            if not business:
                db.session.add(Business(
                    code_pairing=code_pairing, name=name, type_deploy=type_deploy,date_expire=date_expire)
                )
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{name} was added!'
                return response_object, 201
            else:
                response_object['message'] = 'Sorry. Business Name already exists.'
                return response_object, 400
        except (exc.IntegrityError, ValueError):
            db.session.rollback()
            return response_object, 400

    def get(self):
        """Obtener todos los usuarios"""
        response_object = {
            'status': 'success',
            'data': {
                'business': [business.to_json() for business in Business.query.all()]
            }
        }
        return response_object, 200

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

api.add_resource(HuamiCallback, '/xiaomi/callback') #web login
#Api login
api.add_resource(HuamiCallbackApi, '/api/auth/xiaomi/')

api.add_resource(HuamiCallbackApiRegister, '/api/auth/xiaomi/register')
# device API
api.add_resource(DeviceCallbackApi, '/api/device')
#api.add_resource(HuamiCallbackApiRegister, '/api/device/update')
#api.add_resource(HuamiCallbackApiRegister, '/api/device/delete')
# business API
api.add_resource(BusinessCallbackApi, '/api/business')
#api.add_resource(HuamiCallbackApiRegister, '/api/business/update')
#api.add_resource(HuamiCallbackApiRegister, '/api/business/delete')
# user API
api.add_resource(UserCallbackApi, '/api/user')
api.add_resource(UserPairingCallbackApi, '/api/user/pairing')
#api.add_resource(HuamiCallbackApiRegister, '/api/user/delete')


@users_blueprint.route('/', methods=['GET'])
def index():
    #return render_template('index.html')
    response_object = {
            'status': 'success',
            'message': 'Api Auth Xiaomi'
        }
    return response_object, 200

@users_blueprint.route('/xiaomi/activate', methods=['GET'])
def index():
    return render_template('index.html')