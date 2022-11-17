# Desarrollo de software en la nube - Grupo 18
Esta entrega del proyecto, hace referencia a la entrega cuatro: DISEÑO E IMPLEMENTACIÓN DE UNA APLICACIÓN WEB ESCALABLE EN LA NUBE PÚBLICA – ESCALABILIDAD EN EL BACKGROUND.

**Nota:**
Las instrucciones de instalaciones y otros detalles se encuentran la Wiki, Entrega 4 [Aqui.]()<br>
Se debe tener en cuenta que para el correcto funcionamiento del worker, se deben realizar las siguientes instalaciones en las máquinas virtuales.

## Instalaciones Ubuntu:
Se deben realizar las siguientes instalaciones para ejecutar el programa

**Nota:** Estas instrucciones e instalaciones son solo validas para el sistema operativo **Linux Ubuntu**

1. Actualizar paquetes: `sudo apt update`
2. Instalar Python 3.x: `sudo apt install python3`
3. Instalar gestor de paquetes de python: `sudo apt install python3-pip`
4. Instalar gestor de ambientes virtualesde python: `sudo apt install python3-venv`
5. Instalar paquete de flask: `sudo apt install python3-flask`
6. Instalar paquete de audios: `sudo apt install ffmpeg`
7. Instalar Git: `sudo apt install git`

## Instalaciones Windows:
Para esta entrega se puede utilizar de forma local en sistema operativo windows, para ello se debe realizar las siguientes instalaciones

**Nota:** Estas instrucciones e instalaciones son solo validas para el sistema operativo **Windows**

1. Descargar e instalar python 3.9.8: [AQUI](https://www.python.org/downloads/release/python-398/)
2. Descargar e instalar Git: [AQUI](https://git-scm.com/download/win)
3. Descargar e instalar ffmpeg: [AQUI](https://www.wikihow.com/Install-FFmpeg-on-Windows), verificar instalación con: `ffmpeg -version`

## Autenticarse con Gcloud:
Para realizar la autenticación en el equipo local, se debe realizar los siguientes pasos:
1. Descarga el instalador de la CLI de Google Cloud: [AQUI](https://cloud.google.com/sdk/docs/install?hl=es-419#windows). **Nota:** Este proceso puede tomar algunos minutos.
2. Se debe reiniciar el equipo para que se tomen los cambios necesarios.
3. En el proyecto de GCP, en el apartado de "IAM", se debe tener registrado el correo electronico de la persona que va a efectuar los cambios, ya que con este se otorga los permiso para el proyecto, se recomienda que se otorguen todos los permisos con "Owner" del proyecto.
4. Autenticar con el siguiente comando: `gcloud auth login`, esto abrira una ventana del navegador, donde se debe autenticar con las credenciales del correo del punto anterior.
5. Configurar el proyecto con el comando: `gcloud config set project PROYECT_ID`, no olvidar reemplazar "PROYECT_ID", por el ID del proyecto.
6. Obtener las credenciales co el comando: `gcloud auth application-default login`, esto abrira nuevamente una ventana de navegador, donde se debera autenticar el correo el paso dos.
7. Al completar exitosamente todos los pasos anteriores, el ventana de comandos, debería aparecer un mensaje con la ruta donde se guarda las credenciales: `Credentials saved to file: [C:\Users\user\AppData\Roaming\gcloud\application_default_credentials.json]` 
8. Para más información de autenticación ingresar: [AQUI](https://cloud.google.com/sdk/gcloud/reference/auth/login)

