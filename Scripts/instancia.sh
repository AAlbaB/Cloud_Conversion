#!/usr/bin/bash
# -*- coding: utf-8 -*-


​# define las constantes usadas en el script
user=`echo $USER`
group="www-data"
pro_name="Cloud_Conversion"
proyecto="/home/$user/$pro_name"
api="/home/$user/$pro_name/Backend"
url="https://github.com/AAlbaB/Cloud_Conversion.git"
api_service="app"
port="80"
ip=`ip addr | grep "inet " | grep "eth0" | cut -d ' ' -f 6 | cut -d '/' -f 1`

# ----------------------------------------------------------------------------

echo "Inicia la configuración instancia web "`date '+%Y%m%d%H%M%S'`

# +++++++++++++++++++++++++++++++++++​

# Preparar el sistema para la instalación de los servicios.
# actualiza la lista de paquetes en el manejador de paquetes del 
# sistema operativo​

apt-get update -y
# instala los paquetes básicos
apt-get install git python3-venv python3-pip python3-venv python3-flask -y 
apt-get install nginx ffmpeg -y

# +++++++++++++++++++++++++++++++++++​

# establece las credenciales para S3 "POR HACER"
mkdir -p /home/$user/.aws 
echo -e "[default]
aws_access_key_id = AKIA2VWXL5JUUTXUH57Q
aws_secret_access_key = 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
" > /home/$user/.aws/credentials

echo -e "[default]
output = json
region = us-east-1
" > /home/$user/.aws/config

mkdir -p /root/.aws 
echo -e "[default]
aws_access_key_id = AKIA2VWXL5JUUTXUH57Q
aws_secret_access_key = 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
" > /root/.aws/credentials

echo -e "[default]
output = json
region = us-east-1
" > /root/.aws/config


# aws s3 ls s3://bucket-grupo14

# +++++++++++++++++++++++++++++++++++​

# Descarga del repositorio los archivos requeridos
cd /home/$user
git clone $url

# Verificar la existencia de la carpeta del proyecto.
if [ ! -d $proyecto ]; 
then
  # no existe el directorio del repositorio
  echo "Se presento un error en la descarga del repositorio"
  exit 1
fi
# Verifica que se haya descargado la carpeta principal del proyecto
if [ ! -d $Api ];
then
  echo "Se presento un error en la descarga del repositorio"
  exit 2
fi

# actualiza el propietario del proyecto   "POR HACER"
usermod $user -a -G $group
chown -R $user:$group $proyecto
chown -R $user:$group /home/$user/.aws
chmod -R a+rw $proyecto

# +++++++++++++++++++++++++++++++++++​

# Ingresa al directorio donde estan el código de la aplicación
cd $api
# Instala el ambiente virtual
python3 -m venv venv
# Activa el ambiente virtual
source venv/bin/activate
# Instala los paquetes requeridos para el proyecto 
pip install -r requirements.txt  
deactivate
# +++++++++++++++++++++++++++++++++++​

# Crear el servicio de Gunicorn
echo -e "
[Unit]
Description=Gunicorn instance to serve Gunicorn $api_service
After=network.target
[Service]
User=$user
Group=$group
WorkingDirectory=$api
Environment='PATH=$api/venv/bin'
ExecStart=$api/venv/bin/gunicorn --workers 4 --bind unix:$api_service.sock -m 007 wsgi:app
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/$api_service.service

# +++++++++++++++++++++++++++++++++++​

# elimina el sitios por default habilitado en Nginx
rm -f /etc/nginx/sites-enabled/default
# crea el servicio de Nginx
echo -e "
server {
    listen $port;
    server_name $ip;
    client_max_body_size 100M;
    location / {
        include proxy_params;
        proxy_pass http://unix:$api/$api_service.sock;
    }
}" > /etc/nginx/sites-enabled/$api_service

# +++++++++++++++++++++++++++++++++++​

# Iniciar los servicios instalados.
systemctl start app
systemctl enable app
systemctl restart nginx

echo "Instalación terminada "`date '+%Y%m%d%H%M%S'`