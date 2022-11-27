import os
import logging
from datetime import datetime
from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.modelos import File, User
from api.utils import send_email
from google.cloud import storage
from google.cloud import pubsub_v1

load_dotenv()
client = storage.Client(project = os.getenv('PROYECT_STORAGE'))
bucket = client.get_bucket(os.getenv('BUCKET'))

credentials_path = os.getcwd() + '/' + os.getenv('LOCAL_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

timeout = 5.0
subscriber = pubsub_v1.SubscriberClient()
subs_login = os.getenv('SUBSCRIPTION_LOGIN')
subs_converter = os.getenv('SUBSCRIPTION_CONVERSION')

PATH_LOGIN = os.getcwd() + '/logs/log_login.log'
PATH_CONVERT = os.getcwd() + '/logs/log_convert.log'
RUTA_CONVERTIDA = os.getcwd() + '/files/convertido'
RUTA_ORIGINALES = os.getcwd()

load_engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind = load_engine)
session = Session()

def registrar_log(message):   
    user = message.attributes.get('username')
    date = message.attributes.get('date')
    log_login.info('El usuario: {}, ha iniciado sesion'.format(user))
    print('-> El usuario: {}, ha iniciado sesión: {}'.format(user, date))
    message.ack()

def convert_music(message):
    
    try:
        old_format = message.attributes.get('old_format')
        new_format = message.attributes.get('new_format')
        file_origen = message.attributes.get('file_origen')
        file_destino = message.attributes.get('file_destino')
        task_id = message.attributes.get('task_id')

    except Exception as e:
        print ('-> A ocurrido un error obteniendo los datos de la tarea: ' + str(e))

    try: 
        blob = bucket.blob('originales/' + file_origen)
        blob.download_to_filename(file_origen)
        origin_path = RUTA_ORIGINALES + '/' + file_origen
        converter_path = RUTA_CONVERTIDA + '/' + file_destino
        new_task = session.query(File).get(task_id)

        if old_format == "mp3":
            sound = AudioSegment.from_mp3(origin_path)
            sound.export(converter_path, format = new_format)           
            new_task.status = 'processed'
            session.commit()

        elif old_format == "ogg":
            sound = AudioSegment.from_ogg(origin_path)
            sound.export(converter_path, format = new_format)
            new_task.status = 'processed'
            session.commit()

        elif old_format == "wav":
            sound = AudioSegment.from_wav(origin_path)
            sound.export(converter_path, format = new_format)
            new_task.status = 'processed'
            session.commit()

        else:
            print ('No se proporciono una extension valida {}'.format(old_format))

        print ('-> El audio {}, se convirtio a : {}'.format(file_origen, new_format))    
        mensaje = 'El audio {}, se convirtio a : {}'.format(file_origen, new_format)

    except Exception as e:
            print ('\n-> A ocurrido un error convirtiendo el archivo ' + str(e))
            mensaje = 'A ocurrido un error convirtiendo el archivo ' + str(e)
    
    log_convert.info('Para la tarea con Id: {}, Se registro: {}'.format(task_id, mensaje))
    
    try:
        os.remove(origin_path)
        blob = bucket.blob('convertido/' + file_destino)
        blob.upload_from_filename(converter_path)
        urlfile = blob.public_url
        new_task.pathConvertido = urlfile
        session.commit()
        os.remove(converter_path)
        print('-> Se subio el audio convertido: {}'.format(file_destino))
        mensaje = 'Se subio el audio convertido: {}'.format(file_destino)
        
    except Exception as e:
        print ('-> A ocurrido un error subiendo el archivo convertido: ' + str(e))
        mensaje = 'A ocurrido un error subiendo el archivo convertido: ' + str(e)
         
    log_convert.info('Para la tarea con Id: {}, Se registro: {}'.format(task_id, mensaje))
                            
    try: 
        user = session.query(User).get(new_task.user)
        send_email(user.email, new_task.fileName, new_task.newFormat)
        mensaje = 'Se envio un email al usuario: {}'.format(user.username)

    except Exception as e:
        mensaje = 'A ocurrido un error en el envio del email ' + str(e)
        
    log_convert.info('Para la tarea con Id: {}, Se registro: {}'.format(task_id, mensaje))
    message.ack()

def setup_logger(name, log_file, level=logging.INFO):

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Cola de tareas para conversión de audios
log_convert = setup_logger('log_convert', PATH_CONVERT)
pull_converter = subscriber.subscribe(subs_converter, callback=convert_music)
print(f'Listening for messages on {subs_converter}')

# Cola de tareas para registro de inicio de sesión
log_login = setup_logger('log_login', PATH_LOGIN)
pull_login = subscriber.subscribe(subs_login, callback=registrar_log)
print(f'Listening for messages on {subs_login}')

with subscriber:
    try:
        pull_login.result()
        pull_converter.result()
    except TimeoutError:
        pull_login.cancel()
        pull_login.result()
        pull_converter.cancel()
        pull_converter.result()

    

