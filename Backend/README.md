# Ejecución de la aplicación LOCAL
En esta serie de instrucciones, se podrá ejecutar la aplicación de forma local en los sistemas operativos Linux-Ubuntu y Windows

## Obtener credenciales
1. Crear cola de mensajes con el publicador y suscritor en la sección de GCP -"PUB/SUB"
2. Crear una nueva cuenta de servicio para poder realizar las publicaciones, la sección de GCP "IAM", Service Accounts, Create Service Account
3. Asignar un nombre, descripción y en la sección "Grant this service account access to project" buscar PUB/SUB y seleccionar el rol "PUB/SUB Admin"
4. Por último, cuando se crea la nueva cuenta, ingresar a ella y en la sección de "Keys", añadir una nueva en formato JSON
5. Esta Key se descarga automáticamente y es la que podemos usar de forma local para usar PUB/SUB y colocarle el nombre de "cloud-conversio-test"
6. En el archivo tareas.py y vistas.py, descomentar las lineas 17 a 19
7. Para más información revisar el video: [Set up & use PubSub with Python](https://www.youtube.com/watch?v=xOtrCmPjal8&ab_channel=D-I-Ry)

## Ejecutar aplicacion en Ubuntu (Local)
Primero se debe realizar la instalación de algunos programas, para ello revisar el README de la raiz del proyecto.
Para el correcto funcionamiento del programa, se debe crear un ambiente virtual e instalar unos paquetes

### Preparar ambiente virutal (Estar en carpeta Backend)
1. Crear ambiente virtual en carpeta Backend:`python3 -m venv venv`
2. Activar ambiente virtual: `source venv/bin/activate`
3. Validar en la consola que se tiene activo el ambiente virtual, para desactivar env: `deactivate`
4. Instalar requirements: `python3 -m pip install -r requirements.txt`

### Correr programa
**Importante:** Verificar que el entorno virtual este activado y verificar las conexiones a base de datos en el archivo .env
1. En una consola desde la carpeta Backend: `flask run`, se debería habilitar: `Running on http://127.0.0.1:5000`
2. En otra consola desde la carpeta Backend: `python3 tareas.py`, aparece un mensaje de que escucha los mensajes de PUB/SUB.
3. Para dejar de escuchar los mensajes, salir con: `CTRL + C`

## Ejecutar aplicacion en Windows (Local)
Primero se debe realizar la instalación de algunos programas, para ello revisar el README de la raiz del proyecto.
Para la cuarta entrega entrega, se puede utilizar Windows, para esto seguir las siguientes instrucciones:

### Preparar ambiente virutal (Estar en carpeta Backend)
1. Crear ambiente virtual en carpeta Backend: `python -m venv venv`
2. Activar ambiente virtual: `venv/Scripts/activate`
3. En caso de tener problemas con activar el entorno virtual, se debe abrir el PowerShell como administrador y ejecutar el siguiente comando:  `Set-ExecutionPolicy RemoteSigned -Force`
4. Instalar requirements: `pip install -r requirements.txt`

### Correr programa
**Importante:** Verificar que el entorno virtual este activado y verificar las conexiones a base de datos en el archivo .env
1. En una consola desde la carpeta Backend: `flask run`, se debería habilitar: `Running on http://127.0.0.1:5000`
2. En otra consola desde la carpeta Backend: `python tareas.py`, aparece un mensaje de que escucha los mensajes de PUB/SUB.


