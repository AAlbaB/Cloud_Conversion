from celery import Celery
from pydub import AudioSegment

celery_app = Celery(__name__, broker = 'redis://localhost:6379/0')

@celery_app.task(name = 'registrar_log')
def registrar_log(usuario, fecha):
    with open('log_signin.txt', 'a+') as file:
        file.write('{} - inicio de sesion: {}\n'.format(usuario, fecha))

@celery_app.task(name = 'convertir_audio')
def convert_music(origin_path, dest_path, origin_format, new_format):

    if origin_format == "mp3":
        sound = AudioSegment.from_mp3(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(origin_path, new_format))

    elif origin_format == "ogg":
        sound = AudioSegment.from_ogg(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(origin_path, new_format))

    elif origin_format == "wav":
        sound = AudioSegment.from_wav(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(origin_path, new_format))

    else:
        print ('Ocurrio un error en la conversion')
