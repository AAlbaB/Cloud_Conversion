#!/usr/bin/bash
# -*- coding: utf-8 -*-

# Define constantes usadas en el script
user=`echo $USER`
group="www-data"
name_proyecto="Cloud_Conversion"
path_proyecto="/home/$user/$name_proyecto"
path_api="/home/$user/$name_proyecto/Backend"
url="https://github.com/AAlbaB/Cloud_Conversion.git"
api_service="app"
port="8080"
ip=`ip a | grep "inet " | grep "inet 10" | cut -d ' ' -f 6 | cut -d '/' -f 1`

# ----------------------------------------------------------------------------

echo "Inicia la configuración instancia web "`date '+%Y%m%d%H%M%S'`

# Se debe tener presente que esta instalación se debe realizar sobre una instancia que previamente, tenga instalado los paquetes del README

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

# Establecemos variables de entorno en la aplicación
export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

deactivate

# Crear el servicio de Gunicorn
echo "
[Unit]
Description=Gunicorn instance to serve Gunicorn $api_service
After=network.target

[Service]
User=$user
Group=$group
WorkingDirectory=$path_api
Environment='PATH=$path_api/venv/bin'
ExecStart=$path_api/venv/bin/gunicorn --workers 4 --bind unix:$api_service.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/$api_service.service

sudo systemctl start app
sudo systemctl enable app

# crea el servicio de Nginx
echo "
server {
    listen $port;
    server_name $ip;
    client_max_body_size 100M;

    location / {
        include proxy_params;
        proxy_pass http://unix:$path_api/$api_service.sock;
    }
}" > /etc/nginx/sites-available/$api_service

sudo ln -s /etc/nginx/sites-available/$api_service /etc/nginx/sites-enabled
sudo systemctl restart nginx

echo "Web server desplegado: "`date '+%Y%m%d%H%M%S'`