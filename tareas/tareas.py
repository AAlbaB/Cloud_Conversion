from celery import Celery
from pydub import AudioSegment

celery_app = Celery(__name__, broker = 'redis://localhost:6379/0')

@celery_app.task(name = 'registrar_log')
def registrar_log(usuario, fecha):
    with open('log_signin.txt', 'a+') as file:
        file.write('{} - inicio de sesion: {}\n'.format(usuario, fecha))

@celery_app.task(name = 'convertir_audio')
def convert_music(origin_path, dest_path, new_format):
    sound = AudioSegment.from_mp3(origin_path)
    sound.export(dest_path, format = new_format)
    print ('\n-> El archivo {}, se convirtio a : {}'.format(origin_path, new_format))