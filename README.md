# Desarrollo de software en la nube - Grupo 18
Esta entrega del proyecto, hace referencia a la entrega cinco: MIGRACIÓN DE UNA APLICACIÓN WEB A UNA PLATAFORMA PAAS EN LA NUBE PÚBLICA.

**Nota:**
Las instrucciones de instalaciones y otros detalles se encuentran la Wiki, Entrega 5 [Aqui.](https://github.com/AAlbaB/Cloud_Conversion/wiki/Instalaci%C3%B3n-Plataforma-PAAS)<br>
Se debe tener en cuenta que para el correcto funcionamiento del worker, se deben realizar las siguientes instalaciones en las máquinas virtuales.

## Instalaciones Ubuntu:
Se deben realizar las siguientes instalaciones para ejecutar el programa

**Nota:** Estas instrucciones e instalaciones son solo validas para el sistema operativo **Linux Ubuntu**

1. Actualizar paquetes: `sudo apt update`
2. Instalar Python 3.x: `sudo apt install python3`
3. Instalar gestor de paquetes de python: `sudo apt install python3-pip`
4. Instalar gestor de ambientes virtualesde python: `sudo apt install python3-venv`
5. Instalar paquete de flask: `sudo apt install python3-flask`
6. Instalar paquete de audios: `sudo apt install ffmpeg`, para la entrega cinco se utilizo un contenedor de Docker con esta instalación, debido a que por defecto Python no tiene esta instalación.
7. Instalar Git: `sudo apt install git`

## Autenticarse con GCLOUD:
Para realizar la autenticación en el equipo local, se debe realizar los siguientes pasos:
1. Descarga el instalador de la CLI de Google Cloud: [AQUI](https://cloud.google.com/sdk/docs/install?hl=es-419#windows).<br> 
**Nota:** Este proceso puede tomar algunos minutos, para el caso en el cual se deba autenticar desde la consola de GCP, no es necesario descargar el CLI de Google Cloud y puede pasar al punto 3.
2. Se debe reiniciar el equipo para que se tomen los cambios necesarios.
3. En el proyecto de GCP, en el apartado de "IAM", se debe tener registrado el correo electronico de la persona que va a efectuar los cambios, ya que con este se otorga los permiso para el proyecto, se recomienda que se otorguen todos los permisos con "Owner" del proyecto.
4. Autenticar con el siguiente comando: `gcloud auth login`, esto abrira una ventana del navegador, donde se debe autenticar con las credenciales del correo del punto anterior.
5. Configurar el proyecto con el comando: `gcloud config set project PROYECT_ID`, no olvidar reemplazar "PROYECT_ID", por el ID del proyecto.
6. Obtener las credenciales co el comando: `gcloud auth application-default login`, esto abrira nuevamente una ventana de navegador, donde se debera autenticar el correo el paso dos.
7. Al completar exitosamente todos los pasos anteriores, el ventana de comandos, debería aparecer un mensaje con la ruta donde se guarda las credenciales: `Credentials saved to file: [C:\Users\user\AppData\Roaming\gcloud\application_default_credentials.json]` 
8. Para más información de autenticación ingresar: [AQUI](https://cloud.google.com/sdk/gcloud/reference/auth/login)

