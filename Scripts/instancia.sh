#!/usr/bin/bash
# -*- coding: utf-8 -*-

# Define constantes usadas en el script
user=`echo $USER`
name_proyecto="Cloud_Conversion"
path_proyecto="/home/$user/$name_proyecto"
path_api="/home/$user/$name_proyecto/Backend"
url="https://github.com/AAlbaB/Cloud_Conversion.git"
ip=`ip a | grep "inet " | grep "inet 10" | cut -d ' ' -f 6 | cut -d '/' -f 1`

# ----------------------------------------------------------------------------

echo "Inicia la configuración instancia web "`date '+%Y%m%d%H%M%S'`

# Preparar el sistema para la instalación de los servicios de paquetes basicos

apt-get update -y
apt-get install python3 python3-pip  python3-flask -y 
apt-get install git ffmpeg ufw -y

# Descarga del repositorio los archivos requeridos
mkdir -p /home/$user
cd /home/$user
git clone $url

# Verificar la existencia de la carpeta del proyecto.
if [ ! -d $path_proyecto ]; 
then
  # no existe el directorio del repositorio
  echo "Se presento un error en la descarga del repositorio"
  exit 1
fi
# Verifica que se haya descargado la carpeta principal del proyecto
if [ ! -d $path_api ];
then
  echo "No existe la API del proyecto"
  exit 2
fi

# Ingresa al directorio donde estan el código de la aplicación
cd $path_api
# Instala los paquetes requeridos para el proyecto 
pip install -r requirements.txt 

# Desplegamos la aplicación en ambiente de desarrollo
export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

echo "Web server desplegado, para detener CTRL + C: "`date '+%Y%m%d%H%M%S'`
# Habilitamos el puerto 5000 de la aplicación
sudo ufw allow 5000
gunicorn --bind 0.0.0.0:5000 wsgi:app