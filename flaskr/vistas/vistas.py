import re
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required
from flask import request
from ..modelos import db, User, UserSchema, File, FileSchema

user_schema = UserSchema()
file_schema = FileSchema()

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
                    return {'mensaje': 'Contaseñas debe contener minusculas, mayusculas y numeros'}, 401

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
                    token_de_acceso = create_access_token(identity = usuario.username)
                    return {'mensaje':'Inicio de sesión exitoso',
                            'token': token_de_acceso}, 200
                            
                else:
                    return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401
            
            except Exception as e:
                return {'mensaje': 'A ocurrido un error, por favor vuelve a intentar'}, 503

