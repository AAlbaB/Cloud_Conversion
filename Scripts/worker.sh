#!/usr/bin/bash
# -*- coding: utf-8 -*-

# Define constantes usadas en el script
user=`echo $USER`
name_proyecto="Cloud_Conversion"
path_proyecto="/home/$user/$name_proyecto"
path_api="/home/$user/$name_proyecto/Backend"
url="https://github.com/AAlbaB/Cloud_Conversion.git"

# ----------------------------------------------------------------------------

echo "Inicia la configuración instancia web "`date '+%Y%m%d%H%M%S'`

# Preparar el sistema para la instalación de los servicios de paquetes basicos

apt-get update -y
apt-get install python3 python3-venv python3-pip python3-dev python3-flask -y 
apt-get install git ffmpeg redis-server -y

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
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Worker desplegado: "`date '+%Y%m%d%H%M%S'`
