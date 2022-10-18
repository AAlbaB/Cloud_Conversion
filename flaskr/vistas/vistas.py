from flask_restful import Resource
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
        return 'Operacion Exitossa', 204

class VistaSignIn(Resource):

    def post(self):
        user_username = User.query.filter(User.username == request.json['username']).first()
        user_email = User.query.filter(User.email == request.json['email']).first()

        if user_username and user_email is None:
            try:
                new_user = User(username = request.json['username'], 
                                        password = request.json['password'], 
                                        email =request.json['email'])
                
                db.session.add(new_user)
                db.session.commit()

                return {'message': 'Usuario creado exitosamente', 
                        'id': new_user.id, 'usuario': new_user.username, 
                        'email': new_user.email}

            except Exception as e:
                return {'message': 'A ocurrido un error, por favor vuelve a intentar'}, 401
        else:
            return {'message': 'Usuario ya existe, por favor iniciar sesión'}, 202

class VistaLogIn(Resource):
    def post(self):
            log_username = request.json['username']
            log_passsword = request.json['password']
            usuario = User.query.filter_by(username = log_username, password = log_passsword).all()
            if usuario:
                return {'mensaje':'Inicio de sesión exitoso'}, 200
            else:
                return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401
