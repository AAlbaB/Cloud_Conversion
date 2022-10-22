import re
import os
from sqlalchemy import desc
from datetime import datetime
from celery import Celery
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import request
from ..modelos import db, User, UserSchema, File, FileSchema
from werkzeug.utils import secure_filename

celery_app = Celery(__name__, broker = 'redis://localhost:6379/0')
user_schema = UserSchema()
file_schema = FileSchema()

#RUTA_CONVERTIDA = '../Backend/Files/convertido'
#RUTA_ORIGINALES = '../Backend/Files/originales'

RUTA_CONVERTIDA = '/home/andresalba/Escritorio/Cloud_Conversion/Backend/Files/convertido'
RUTA_ORIGINALES = '/home/andresalba/Escritorio/Cloud_Conversion/Backend/Files/originales'
FORMATOS = ["mp3", "ogg", "wav"]

@celery_app.task(name = 'registrar_log')
def registrar_log(*args):
    pass

@celery_app.task(name = 'convertir_audio')
def convertir_audio(*args):
    pass

def validate_password(password):
    if 8 <= len(password) <= 24:
        if re.search('[a-z]', password) and re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                return True
    
    return False

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

class VistaTasksUser(Resource):

    @jwt_required()
    def post(self):
        # Crea una nueva tarea de conversion a un usario autenticado
        # Endpoint http://localhost:5000/api/tasks

        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id
        user_name = user.username

        if db.session.query(User.query.filter(User.id == user_id).exists()).scalar():

            try:
                file = request.files['fileName']
            except:
                return {'mensaje':'Error: Cargar archivo a convertir'}, 400

            try:
                new_format = request.form['newFormat']
            except:
                return {'mensaje':'Error: Definir extension de destino'}, 400

            if (file is None) or (new_format is None): 
                return {'mensaje':'Error: Revisar parametros de ingreso'}, 400

            converter_file = secure_filename(file.filename)
            old_format = converter_file.split('.')[-1].lower()
            base_file = converter_file[:(len(converter_file) - len(old_format) - 1)]
            new_format = new_format.lower()

            if len(base_file) == 0: 
                return {'mensaje':'Error: Nombre archivo sin base'}, 400
            
            if old_format not in FORMATOS:
                return {'mensaje':'Error: Formato origen no valido (wav, ogg, mp3)'}, 400

            if new_format not in FORMATOS:
                return {'mensaje':'Error: Formato destino no valido (wav, ogg, mp3)'}, 400

            date_actual = datetime.now()
            date_actual = date_actual.strftime('%d%m%Y%H%M%S')

            file_origen = f'{user_name}_{date_actual}_{converter_file}'.replace(' ','_')
            path_origen = f'{RUTA_ORIGINALES}/{file_origen}'

            file_destino = f'{user_name}_{date_actual}_{base_file}.{new_format}'.replace(' ','_')
            path_destino = f'{RUTA_CONVERTIDA}/{file_destino}'

            try:
                file.save(path_origen)
            except:
                return {'mensaje':'Error: al almacenar archivo original'}

            new_task = File(fileName = file_origen, 
                            newFormat = new_format)

            user = User.query.get_or_404(user_id)
            user.files.append(new_task)
            db.session.commit()

            task_id = new_task.id
            args = (path_origen, path_destino, old_format, new_format, file_origen, task_id)
            convertir_audio.apply_async(args = args)

            return file_schema.dump(new_task)

        else:
            return {'mensaje':'Erro: Autenticar usuario'}, 400
        
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
                lista.append({'id': ta.id, 'timeStamp': (ta.timeStamp).strftime('%d%m%Y%H%M%S'),
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