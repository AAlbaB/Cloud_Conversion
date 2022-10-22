## Instalaciones:
Se deben realizar las siguientes instalaciones para ejecutar el programa
1. Actualizar paquetes: `sudo apt-get update`
2. Python 3.x: `sudo apt-get install python3`
3. Gestor de paquetes: `sudo apt-get install python3-pip`
4. Gestor de ambientes virtuales: `sudo apt-get install python3-venv`
5. Instalar paquete de flask: `sudo apt-get install python3-flask`
6. Servidor de redis: `sudo apt-get install redis-server` y `sudo systemctl enable redis-server.service`
7. Paquete de audios: `sudo apt-get install ffmpeg`

## Ejecutar aplicacion:
Para el correcto funcionamiento del programa, se debe crear un ambiente virtual e instalar unos paquetes
### Preparar ambiente virutal (Estar en carpeta Backend):
1. Crear ambiente virtual en carpeta Backend:`python3 -m venv venv`
2. Activar ambiente virtual: `source venv/bin/activate`
3. Validar en la consola que se tiene activo el ambiente virtual, para desactivar env: `deactivate`
4. Instalar requirements: `python3 -m pip install -r requirements.txt`
5. Verificar funcionalidad de redis: `redis-server`
6. Validar que redis este en ejecucion (salir con Q): `sudo systemctl status redis`

### Correr programa:
1. En una consola: `cd api/tareas` y `celery -A tareas worker -l info`
2. En otra consola: `cd Backend` y `flask run` (Verificar que el entorno virtual este activado)