import os
from datetime import datetime
from celery import Celery
from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.modelos import File, User
from api.utils import send_email

PATH_LOGIN = os.getcwd() + '/logs/log_login.txt'
PATH_CONVERT = os.getcwd() + '/logs/log_convert.txt'

load_dotenv()
celery_app = Celery('__name__', broker = os.getenv('BROKER_REDIS'))
load_engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind = load_engine)
session = Session()

@celery_app.task(name = 'registrar_login')
def registrar_log(usuario, fecha):
    with open(PATH_LOGIN, 'a+') as file:
        file.write('El usuario: {} - Inicio sesion: {}\n'.format(usuario, fecha))

@celery_app.task(name = 'convert_music')
def convert_music(origin_path, dest_path, origin_format, new_format, name_file, task_id):

    new_task = session.query(File).get(task_id)

    if origin_format == "mp3":
        sound = AudioSegment.from_mp3(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        session.commit()

    elif origin_format == "ogg":
        sound = AudioSegment.from_ogg(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        session.commit()

    elif origin_format == "wav":
        sound = AudioSegment.from_wav(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        session.commit()

    else:
        print ('No se proporciono una extension valida {}'.format(name_file))

    registrar_conversion(task_id, '-> El audio {}, se convirtio a : {}'.format(name_file, new_format),  
                            datetime.utcnow())
                            
    try: 
        user = session.query(User).get(new_task.user)
        send_email(user.email, new_task.fileName, new_task.newFormat)
        mensaje = '-> Se envio un email al usuario: {}'.format(user.username)
    except Exception as e:
        mensaje = '-> A ocurrido un error en el envio del email'

    registrar_conversion(task_id, mensaje, datetime.utcnow())

def registrar_conversion(id_task, mensaje, fecha):
    with open(PATH_CONVERT, 'a+') as file:
        file.write('Para la tarea con Id: {}, Se registro: {} - Con fecha: {}\n'.format(id_task, mensaje, fecha))



    

