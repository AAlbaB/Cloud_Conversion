## Despliegue Maquina Virtual:
Se deben realizar los siguientes pasos para el despliegue de la maquina virtual

1. Descargue la VM desde  el siguiente link: [Maquina Virtual](https://uniandes.sharepoint.com/:u:/s/EquipodeestudioMISO/EfASTO5VwCxHln0rYOpQkW4BEHy7b15iDFrGnx0Pw_F6oA?e=T3pI9I)  
2. Importe la VM en VirtualBox  `Version VirtualBox 7.0`
3. ingrese las credenciales de la VM  `Username:miso  | Password:miso123`
4. Digite en la consola de linux el siguiente comando: `tmux`
5. Cree dos terminales más con el siguiente comando. `ctrl B C `
6. Para cambiar entre terminales use el comando `ctrl B numero_de_terminal`
7. Ejecute los siguientes comandos en la terminal especificada.
    
### Terminal  0
	`sudo systemctl enable redis-server.service`
	`redis-server`

### Terminal 1
	`cd Cloud_Conversion/Backend`    
	`source lab-flask/bin/activate`
	`celery -A tareas worker -l info`

### Terminal 2
	`ip a`  para conocer la ip a la cual conectarse una vez el servidor es corriendo. 
	`cd Cloud_Conversion/Backend`   
	`source lab-flask/bin/activate`
	`gunicorn --bind 0.0.0.0:5000 wsgi:app`
