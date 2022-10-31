# Desarrollo de software en la nube - Grupo 18
Esta entrega del proyecto es el despliegue de la API en instancias de  GCP. El despliegue se realió con el servidor de aplicaciones gunicorn y nginx como servidor proxy.

**Nota:**
Las instrucciones de instalaciones y otros detalles se encuentran la Wiki, entrega 2.[Aqui](https://github.com/AAlbaB/Cloud_Conversion/wiki/Instalaci%C3%B3n--de-migraciones) 
Se debe tener en cuenta que para el correcto funcionamiento del worker y web-server, se deben realizar las siguientes instalaciones en las máquinas virtuales.

## Instalaciones
Se deben realizar las siguientes instalaciones para ejecutar el programa

**Nota:** Estas instrucciones e instalaciones son solo validas para instalacion en sistema operativo **Linux Ubuntu**

1. Actualizar paquetes: `sudo apt update`
2. Instalar Python 3.x: `sudo apt install python3`
3. Instalar gestor de paquetes de python: `sudo apt install python3-pip`
4. Instalar gestor de ambientes virtualesde python: `sudo apt install python3-venv`
5. Instalar paquete de flask: `sudo apt install python3-flask`
6. Instalar servidor de redis: `sudo apt install redis-server` y `sudo systemctl enable redis-server.service`
7. Instalar paquete de audios: `sudo apt install ffmpeg`
8. Instalar Git: `sudo apt install git`
