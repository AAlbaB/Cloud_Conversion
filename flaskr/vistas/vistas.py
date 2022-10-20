import re
import os
from datetime import datetime
from celery import Celery
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required
from flask import request
from ..modelos import db, User, UserSchema, File, FileSchema

celery_app = Celery(__name__, broker = 'redis://localhost:6379/0')
user_schema = UserSchema()
file_schema = FileSchema()

@celery_app.task(name = 'registrar_log')
def registrar_log(*args):
    pass

@celery_app.task(name = 'convertir_audio')
def convertir_audio(*args):
    pass

class VistaUsers(Resource):

    def get(self):
        return [user_schema.dump(user) for user in User.query.all()]

class VistaUser(Resource):
    
    def get(self, id_user):
        return user_schema.dump(User.query.get_or_404(id_user))

    def put(self, id_user):
        user = User.query.get_or_404(id_user)
        user.password = request.json.get('password', user.password)
        db.session.commit()
        return user_schema.dump(user)

    def delete(self, id_user):
        user = User.query.get_or_404(id_user)
        db.session.delete(user)
        db.session.commit()
        return 'Operacion Exitosa', 204

def validate_password(password):
    if 8 <= len(password) <= 24:
        if re.search('[a-z]', password) and re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                return True
    
    return False

class VistaSignIn(Resource):

    def post(self):

        user_username = User.query.filter(User.username == request.json['username']).first()
        user_email = User.query.filter(User.email == request.json['email']).first()
        first_pass = request.json['password']
        second_pass = request.json['password_again']

        if (user_username is None) and (user_email is None):

            if first_pass == second_pass:

                if validate_password(first_pass):

                    try:
                        new_user = User(username = request.json['username'], 
                                                password = request.json['password'], 
                                                email =request.json['email'])
                        
                        db.session.add(new_user)
                        db.session.commit()

                        return {'mensaje': 'Usuario creado exitosamente', 
                                'id': new_user.id, 'usuario': new_user.username, 
                                'email': new_user.email}, 200

                    except Exception as e:
                        return {'mensaje': 'A ocurrido un error, por favor vuelve a intentar'}, 503
                
                else:
                    return {'mensaje': 'Contaseñas debe contener minusculas, mayusculas y numeros'}, 400

            else:
                return {'mensaje': 'Contaseñas no coinciden, por favor vuelve a intentar'}, 401

        else:
            return {'mensaje': 'Usuario ya existe, por favor iniciar sesión'}, 203


class VistaLogIn(Resource):

    def post(self):

            try:
                usuario = User.query.filter(User.username == request.json['username'],
                                            User.password == request.json['password']).first()

                if usuario:
                    args = (request.json['username'], datetime.utcnow())
                    registrar_log.apply_async(args = args)
                    token_de_acceso = create_access_token(identity = usuario.username)
                    return {'mensaje':'Inicio de sesión exitoso',
                            'token': token_de_acceso}, 200
                            
                else:
                    return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401
            
            except Exception as e:
                return {'mensaje': 'A ocurrido un error, por favor vuelve a intentar'}, 503

class VistaFilesUser(Resource):

    @jwt_required()
    def post(self, id_user):

        origin_path = request.json['fileName']
        new_format = request.json['newFormat']
        new_path = 'convertido'
        formatos = ["mp3", "ogg", "wav"]

        if os.path.exists(origin_path):

            old_path = origin_path.split("/")
            len_split = len(old_path)
            name_file = old_path[len_split - 1].split(".")[0]
            origin_format = old_path[len_split - 1].split(".")[1]

            if origin_format in formatos:

                if new_format in formatos:

                    new_file = File(fileName = origin_path, newFormat = new_format)
                    user = User.query.get_or_404(id_user)
                    user.files.append(new_file)
                    db.session.commit()
            
                    dest_path = new_path + '/' + name_file + '.' + new_format
                    args = (origin_path, dest_path, origin_format, new_format)
                    convertir_audio.apply_async(args = args)

                    new_file.status = "processed"
                    db.session.commit()

                    return file_schema.dump(new_file)
                
                else:
                    return {'mensaje': 'El formato destino no es aceptado (mp3, ogg, wav)'}, 400

            else:
                return {'mensaje': 'El formato de origen no es aceptado (mp3, ogg, wav)'}, 400

        else:
            return {'mensaje': 'La ruta de origen no existe, por favor verificar'}, 400
