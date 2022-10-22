import re
import os
from sqlalchemy import desc
from datetime import datetime
from celery import Celery
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
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
                    token_de_acceso = create_access_token(identity = usuario.id)
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

                    new_file = File(fileName = (name_file + "." + origin_format), newFormat = new_format)
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

class VistaTasksUser(Resource):

    @jwt_required()
    def get(self):
        # Retorna todas las tareas de un usuario con parametros
        # Endpoint http://localhost:5000/api/tasks?max=100&order=0
        
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id
            
        max = request.args.get('max', default = 100, type = int)
        order = request.args.get('order', default = 0, type = int)
        if max < 1: 
            return {'mensaje':'El valor pasado en max debe ser un numero entero positivo.'}, 400

        if order not in (0, 1): 
            return {'mensaje':'El valor numerico pasado en order debe ser (0 o 1)'}, 400
            
        if db.session.query(File.query.filter(File.user == user_id).exists()).scalar():
                
            tasks = File.query.filter(File.user == user_id)

            if order == 1: tasks = tasks.order_by(desc(File.id))
            elif order == 0: tasks = tasks.order_by(File.id)

            count = 1
            lista = []
            for ta in tasks:
                lista.append({'id': ta.id, 'timeStamp': (ta.timeStamp).strftime('%d/%m/%Y'),
                        'fileName': ta.fileName, 'newFormat': ta.newFormat,
                        'status': ta.status})

                if count >= max: break
                else: count += 1

            return lista
            
        else: 
            return {'mensaje':'El usuario {} no tiene tareas registradas'.format(user_id)}, 400

class VistaTask(Resource):

    @jwt_required()
    def get(self, id_task):
        # Retorna la tarea con id asigando
        # Endpoint http://localhost:5000/api/tasks/id_task

        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id

        if db.session.query(File.query.filter(File.id == id_task,
            File.user == user_id).exists()).scalar():

            return file_schema.dump(File.query.get_or_404(id_task))

        else:
            return {'mensaje':'La tarea no existe para el usuario'}, 400

    @jwt_required()
    def delete(self, id_task):
        # Elimina la tarea y archivos
        # Endpoint http://localhost:5000/api/tasks/id_task

        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id

        if db.session.query(File.query.filter(File.id == id_task,
            File.user == user_id).exists()).scalar():

            task_delete = File.query.get(id_task)

            #TODO: Implementar borrado de archivo origen
            #os.remove(task_delete.origin_path)

            #TODO: Implmentar borrado si se convirtio
            #if task_delete.status == 'processed':
                #os.remove(task_delete.new_path)

            db.session.delete(task_delete)
            db.session.commit()
            return {'mensaje': 'Tarea eliminiada correctamente'}, 200

        else:
            return {'mensaje':'La tarea no existe para el usuario'}, 400