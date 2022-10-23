from lib2to3.pytree import convert
import re
import os
from sqlalchemy import desc
from datetime import datetime
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import request, send_file
from ..modelos import db, User, UserSchema, File, FileSchema
from werkzeug.utils import secure_filename
from tareas import registrar_log, convert_music

user_schema = UserSchema()
file_schema = FileSchema()

RUTA_CONVERTIDA = '/home/miso/Cloud_Conversion/Backend/Files/convertido'
RUTA_ORIGINALES = '/home/miso/Cloud_Conversion/Backend/Files/originales'
FORMATOS = ['mp3', 'ogg', 'wav']

def validate_password(password):
    if 8 <= len(password) <= 24:
        if re.search('[a-z]', password) and re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                return True
    
    return False

class VistaUsers(Resource):

    def get(self):
        # Retorna todos los usuarios registrados
        # Endpoint http://localhost:5000/users

        return [user_schema.dump(user) for user in User.query.all()]

class VistaUser(Resource):
    
    @jwt_required()
    def get(self, id_user):
        # Retorna un usuario por su id
        # Endpoint http://localhost:5000/users/id_user

        return user_schema.dump(User.query.get_or_404(id_user))

    @jwt_required()
    def put(self, id_user):
        # Actualiza la contraseña de un usuario por su id
        # Endpoint http://localhost:5000/users/id_user

        user = User.query.get_or_404(id_user)
        user.password = request.json.get('password', user.password)
        db.session.commit()
        return user_schema.dump(user)

    @jwt_required()
    def delete(self, id_user):
        # Elimina un usuario por su id
        # Endpoint http://localhost:5000/users/id_user

        user = User.query.get_or_404(id_user)
        db.session.delete(user)
        db.session.commit()
        return 'Operacion Exitosa', 204

class VistaSignIn(Resource):

    def post(self):
        # Crea un usuario en la aplicacion
        # Endpoint http://localhost:5000/auth/signup

        user_username = User.query.filter(User.username == request.json['username']).first()
        user_email = User.query.filter(User.email == request.json['email']).first()

        #TODO: Encriptar contraseñas
        first_pass = request.json['password']
        second_pass = request.json['password_again']

        if user_username is not None:
            return {'mensaje': 'Nombre de usuario ya existe, por favor iniciar sesión'}, 203

        if user_email is not None:
            return {'mensaje': 'Correo electronico ya existe, por favor iniciar sesión'}, 203

        if first_pass != second_pass:
            return {'mensaje': 'Contaseñas no coinciden, por favor vuelve a intentar'}, 401

        if validate_password(first_pass) == False:
            return {'mensaje': 'Contaseñas debe contener minusculas, mayusculas y numeros'}, 400

        try:
            new_user = User(username = request.json['username'], 
                            password = request.json['password'], 
                            email =request.json['email'])
                        
            db.session.add(new_user)
            db.session.commit()

            return {'mensaje': 'Usuario creado exitosamente', 
                    'id': new_user.id, 'usuario': new_user.username, 
                    'email': new_user.email}, 200

        except:
                return {'mensaje': 'A ocurrido un error, por favor vuelve a intentar'}, 503
                               
class VistaLogIn(Resource):

    def post(self):
        # Loguea un usuario en la aplicacion
        # Endpoint http://localhost:5000/auth/login

        try:
            usuario = User.query.filter(User.username == request.json['username'],
                                        User.password == request.json['password']).first()

            if usuario:
                #args = (request.json['username'], datetime.utcnow())
                registrar_log.delay(request.json['username'], datetime.utcnow())
                token_de_acceso = create_access_token(identity = usuario.id)
                return {'mensaje':'Inicio de sesión exitoso',
                            'token': token_de_acceso}, 200
                            
            else:
                return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 401
            
        except:
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

            new_task = File(timeStamp = date_actual,
                            fileName = file_origen, 
                            newFormat = new_format,
                            pathOriginal = path_origen,
                            pathConvertido = path_destino)

            user = User.query.get_or_404(user_id)
            user.files.append(new_task)
            db.session.commit()

            task_id = new_task.id
            convert_music.delay(path_origen, path_destino, old_format, new_format, file_origen, task_id)

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
                lista.append({'id': ta.id, 'timeStamp': ta.timeStamp,
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
    def put(self, id_task):
        # Actualiza la tarea con id asigando
        # Endpoint http://localhost:5000/api/tasks/id_task

        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id
        user_name = user.username

        try:
            new_format = request.form['newFormat']
        except:
            return {'mensaje':'Error: Definir extension de destino'}, 400

        if new_format is None: 
            return {'mensaje':'Error: Revisar parametros de ingreso'}, 400

        new_format = new_format.lower()

        if new_format not in FORMATOS:
                return {'mensaje':'Error: Formato destino no valido (wav, ogg, mp3)'}, 400

        if db.session.query(File.query.filter(File.id == id_task,
            File.user == user_id).exists()).scalar():

            put_task = File.query.get(id_task)

            if new_format == put_task.newFormat:
                return {'mensaje':'Ya se solicito el cambio a ese formato'}, 200

            date_actual = datetime.now()
            date_actual = date_actual.strftime('%d%m%Y%H%M%S')
            file_origen = put_task.fileName

            old_format = file_origen.split('.')[-1].lower()

            file_destino = f'{user_name}_{date_actual}.{new_format}'.replace(' ','_')
            path_destino = f'{RUTA_CONVERTIDA}/{file_destino}'

            try:
                if put_task.status == 'processed':
                    os.remove(put_task.pathConvertido)

                put_task.newFormat = new_format
                put_task.pathConvertido = path_destino
                put_task.status = 'uploaded'
                db.session.commit()

                task_id = put_task.id
                convert_music.delay(put_task.pathOriginal, path_destino, old_format, new_format, file_origen, task_id)

                return {'mensaje':'La tarea fue actualizada para conversion'}, 200

            except:
                return {'mensaje':'Archivos no encontrados'}, 404

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

            try:
                os.remove(task_delete.pathOriginal)

                if task_delete.status == 'processed':
                    os.remove(task_delete.pathConvertido)

                db.session.delete(task_delete)
                db.session.commit()
                return {'mensaje': 'Tarea eliminada correctamente'}, 200

            except:
                return {'mensaje':'Archivos no encontrados'}, 404

        else:
            return {'mensaje':'La tarea no existe para el usuario'}, 400

class VistaFiles(Resource):
    @jwt_required()
    def get(self, fileName):
        # Retorna el archivo convertido
        # Endpoint http://localhost:5000/api/files/fileName

        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        user_id = user.id

        if db.session.query(File.query.filter(File.fileName.contains(fileName),
            File.user == user_id).exists()).scalar():

            task_consulta = File.query.filter(File.fileName.contains(fileName),
            File.user == user_id).order_by(File.id.desc()).first()

            if task_consulta.status == 'processed':
                try:
                    return send_file(task_consulta.pathConvertido)
                except Exception as e:
                    return str(e)
            
            else:
                try:
                    return send_file(task_consulta.pathOriginal)
                except Exception as e:
                    return str(e)
        
        else:
            return {'mensaje':'El archivo no existe para el usuario'}, 400



 
    