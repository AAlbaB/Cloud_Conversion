## Instalar Pydub para convertir archivos de audio:
1. Instalar pydub con: `pip install pydub`
1. Se debe verificar la intalacion de ffprobe osino instalarlo con: `pip install ffprobe`
2. Actualizar paquetes: `sudo apt update`
3. Instalar el paquete faltante: `sudo apt install ffmpeg`

## Instalar requirements:
Eecutar el comando `python3 -m pip install -r requirements.txt`

## Ejecutar aplicacion:
### Instalar paqquete de redis-server usando los siguientes comandos por una sola vez
1. Ejecutar comando: `sudo apt install redis-server`
2. Ejecutar comando: `redis-server`

### Correr Celery
1. cd tareas
2. celery -A tareas worker -l info
3. En otra consola: cd flaskr y flask run

## Activar entorno virtual:
`source venv/bin/activate`
