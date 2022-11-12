import os
from datetime import datetime
from celery import Celery
from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.modelos import File, User
from api.utils import send_email
from google.cloud import storage

load_dotenv()
client = storage.Client(project = os.getenv('utility-subset-367815'))
bucket = client.get_bucket(os.getenv('BUCKET'))

PATH_LOGIN = os.getcwd() + '/logs/log_login.txt'
PATH_CONVERT = os.getcwd() + '/logs/log_convert.txt'
RUTA_ORIGINALES = os.getcwd()

celery_app = Celery('__name__', broker = os.getenv('BROKER_URL_LOCAL'))
load_engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind = load_engine)
session = Session()

@celery_app.task(name = 'registrar_login')
def registrar_log(usuario, fecha):
    with open(PATH_LOGIN, 'a+') as file:
        file.write('El usuario: {} - Inicio sesion: {}\n'.format(usuario, fecha))

@celery_app.task(name = 'convert_music')
def convert_music(path_destino, old_format, new_format, file_origen, file_destino, task_id):
    
    try: 
        blob = bucket.blob('originales/' + file_origen)
        blob.download_to_filename(file_origen)
        origin_path = RUTA_ORIGINALES + '/' + file_origen
        new_task = session.query(File).get(task_id)

        if old_format == "mp3":
            sound = AudioSegment.from_mp3(origin_path)
            sound.export(path_destino, format = new_format)
            print ('\n-> El audio {}, se convirtio a : {}'.format(file_origen, new_format))
            new_task.status = 'processed'
            session.commit()

        elif old_format == "ogg":
            sound = AudioSegment.from_ogg(origin_path)
            sound.export(path_destino, format = new_format)
            print ('\n-> El audio {}, se convirtio a : {}'.format(file_origen, new_format))
            new_task.status = 'processed'
            session.commit()

        elif old_format == "wav":
            sound = AudioSegment.from_wav(origin_path)
            sound.export(path_destino, format = new_format)
            print ('\n-> El audio {}, se convirtio a : {}'.format(file_origen, new_format))
            new_task.status = 'processed'
            session.commit()

        else:
            print ('No se proporciono una extension valida {}'.format(file_origen))
        
        mensaje = '-> El audio {}, se convirtio a : {}'.format(file_origen, new_format)

    except Exception as e:
            print ('\n-> A ocurrido un error convirtiendo el archivo ' + str(e))
            mensaje = '-> A ocurrido un error convirtiendo el archivo ' + str(e)
    
    registrar_conversion(task_id, mensaje, datetime.utcnow())
    
    try:
        os.remove(origin_path)
        blob = bucket.blob('convertido/' + file_destino)
        blob.upload_from_filename(path_destino)
        urlfile = blob.public_url
        new_task.pathConvertido = urlfile
        session.commit()
        os.remove(path_destino)
        
    except Exception as e:
         mensaje = '-> A ocurrido un error subiendo el archivo convertido' + str(e)
         
    registrar_conversion(task_id, mensaje, datetime.utcnow())
                            
    try: 
        user = session.query(User).get(new_task.user)
        send_email(user.email, new_task.fileName, new_task.newFormat)
        mensaje = '-> Se envio un email al usuario: {}'.format(user.username)
    except Exception as e:
        mensaje = '-> A ocurrido un error en el envio del email'

    registrar_conversion(task_id, mensaje, datetime.utcnow())

def registrar_conversion(id_task, mensaje, fecha):
    try: 
        with open(PATH_CONVERT, 'a+') as file:
            file.write('Para la tarea con Id: {}, Se registro: {} - Con fecha: {}\n'.format(id_task, mensaje, fecha))
    except Exception as e:
        print('A ocurrido un error al escribir logs: ' + str(e))


    

