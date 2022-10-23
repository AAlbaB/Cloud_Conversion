from celery import Celery
from pydub import AudioSegment
from api.modelos import File, db, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import smtplib as smtp

celery_app = Celery('__name__', broker = 'redis://localhost:6379/0')

load_engine = create_engine('postgresql://postgres:postgres@localhost:5432/nubecon')
Session = sessionmaker(bind = load_engine)
session = Session()

@celery_app.task
def registrar_log(usuario, fecha):
    with open('log_signin.txt', 'a+') as file:
        file.write('{} - inicio de sesion: {}\n'.format(usuario, fecha))

@celery_app.task
def convert_music(origin_path, dest_path, origin_format, new_format, name_file, task_id):

    new_task = session.query(File).get(task_id)
    #user_id = new_task.user
    #user = session.query(User).get(user_id)
    #email_user = user.email

    if origin_format == "mp3":
        sound = AudioSegment.from_mp3(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        #envio_correo(email_user, name_file, new_format)
        session.commit()

    elif origin_format == "ogg":
        sound = AudioSegment.from_ogg(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        #envio_correo(email_user, name_file, new_format)
        db.session.commit()

    elif origin_format == "wav":
        sound = AudioSegment.from_wav(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        new_task.status = 'processed'
        #envio_correo(email_user, name_file, new_format)
        db.session.commit()

    else:
        print ('Ocurrio un error en la conversion con el archivo {}'.format(name_file))

# Se desactiva envio den correo para pruebas de carga y estres
def envio_correo(corre_usuario, name_file, new_format):
    connection = smtp.SMTP_SSL('smtp.gmail.com', 465)
    email_addr = 'mailtotestandes@gmail.com'
    email_passwd = 'turjcvgttwmpfjri'
    subject = "Archivo convertido exitosamente"
    body = "Su archivo " + name_file +  " ha sido convertido a formato " + new_format
    message = 'Subject: {}\n\n{}'.format(subject, body)
    connection.login(email_addr, email_passwd)
    connection.sendmail(from_addr=email_addr, to_addrs = corre_usuario, msg= message)
    connection.close()