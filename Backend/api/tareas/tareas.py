from celery import Celery
from pydub import AudioSegment
#from ..modelos import File, FileSchema, db

#file_schema = FileSchema()

celery_app = Celery('__name__', broker = 'redis://localhost:6379/0')

@celery_app.task()
def registrar_log(usuario, fecha):
    with open('log_signin.txt', 'a+') as file:
        file.write('{} - inicio de sesion: {}\n'.format(usuario, fecha))

@celery_app.task()
def convert_music(origin_path, dest_path, origin_format, new_format, name_file, task_id):

    #new_task = file_schema.dump(File.query.get_or_404(task_id))
    #new_task = File.query.get_or_404(task_id)
    #print(new_task)

    if origin_format == "mp3":
        sound = AudioSegment.from_mp3(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        #new_task.status = 'processed'
        #db.session.commit()

    elif origin_format == "ogg":
        sound = AudioSegment.from_ogg(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        #new_task.status = 'processed'
        #db.session.commit()

    elif origin_format == "wav":
        sound = AudioSegment.from_wav(origin_path)
        sound.export(dest_path, format = new_format)
        print ('\n-> El audio {}, se convirtio a : {}'.format(name_file, new_format))
        #new_task.status = 'processed'
        #db.session.commit()

    else:
        print ('Ocurrio un error en la conversion con el archivo {}'.format(name_file))
