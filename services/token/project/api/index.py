# services/users/project/api/users.py


from flask import Blueprint, request, render_template
from flask_restful import Resource, Api

from project import db
from project.api.models import User
from sqlalchemy import exc
from project.api.huami_token import HuamiAmazfit

users_blueprint = Blueprint("index", __name__,template_folder='./template')
api = Api(users_blueprint)


class UsersPing(Resource):
    def get(self):
        return {"status": "success", "message": "pong!"}


class UsersList(Resource):
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
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                db.session.add(User(username=username, email=email))
                db.session.commit()
                response_object['status'] = 'success'
                response_object['message'] = f'{email} was added!'
                return response_object, 201
            else:
                response_object['message'] = 'email existe.'
                return response_object, 400
        except exc.IntegrityError:
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


class Users(Resource):
    def get(self, user_id):
        """Obtenga detalles de un solo usuario."""
        response_object = {
            'status': 'fail',
            'message': 'User does not exist'
        }
        try:
            user = User.query.filter_by(id=int(user_id)).first()
            if not user:
                return response_object, 404
            else:
                response_object = {
                    'status': 'success',
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'active': user.active
                    }
                }
                return response_object, 200
        except ValueError:
            return response_object, 404

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
        print(not post_data)
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





api.add_resource(HuamiCallback, '/xiaomi/callback')
api.add_resource(HuamiCallbackApi, '/api/auth/xiaomi/')
api.add_resource(HuamiCallbackApiRegister, '/api/auth/xiaomi/register')


@users_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')