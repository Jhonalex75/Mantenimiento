# Guía de Despliegue en Producción

Esta guía proporciona instrucciones detalladas para desplegar el Sistema de Gestión de Mantenimiento en un entorno de producción.

## Requisitos del Servidor

- **Sistema Operativo**: Linux (Ubuntu 20.04/22.04 recomendado)
- **Python**: 3.8 o superior
- **Base de Datos**: PostgreSQL (recomendado) o MySQL
- **Servidor Web**: Nginx o Apache
- **ASGI Server**: Gunicorn o uWSGI
- **Memoria RAM**: Mínimo 2GB (4GB recomendado)
- **Almacenamiento**: Mínimo 10GB (dependiendo del volumen de datos)

## Configuración del Entorno

### 1. Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Instalar Dependencias del Sistema

```bash
sudo apt install -y python3-pip python3-dev python3-venv \
    build-essential libssl-dev libffi-dev python3-setuptools \
    nginx postgresql postgresql-contrib
```

### 3. Configurar Base de Datos PostgreSQL

```bash
# Iniciar servicio de PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear usuario y base de datos
sudo -u postgres createuser -P mantenimiento_user
sudo -u postgres createdb -O mantenimiento_user mantenimiento_db
```

### 4. Configurar Entorno Virtual

```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/mantenimiento
sudo chown $USER:$USER /var/www/mantenimiento

# Crear y activar entorno virtual
cd /var/www/mantenimiento
python3 -m venv venv
source venv/bin/activate
```

### 5. Instalar la Aplicación

```bash
# Clonar el repositorio (o copiar los archivos)
git clone https://github.com/tu-usuario/mantenimiento.git .

# Instalar dependencias
pip install -e ".[production]"
```

## Configuración de la Aplicación

### 1. Variables de Entorno

Crea un archivo `.env` en el directorio de la aplicación:

```env
FLASK_APP=mantenimiento
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_muy_segura
DATABASE_URI=postgresql://mantenimiento_user:tu_contraseña@localhost/mantenimiento_db
```

### 2. Inicializar la Base de Datos

```bash
flask init-db
```

### 3. Configurar Gunicorn

Crea un archivo `wsgi.py` en el directorio de la aplicación:

```python
from mantenimiento import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

Crea un archivo de servicio para Gunicorn:

```bash
sudo nano /etc/systemd/system/mantenimiento.service
```

Con el siguiente contenido:

```ini
[Unit]
Description=Mantenimiento Gunicorn Service
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/var/www/mantenimiento
Environment="PATH=/var/www/mantenimiento/venv/bin"
ExecStart=/var/www/mantenimiento/venv/bin/gunicorn --workers 3 --bind unix:mantenimiento.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Habilita e inicia el servicio:

```bash
sudo systemctl start mantenimiento
sudo systemctl enable mantenimiento
```

### 4. Configurar Nginx

Crea un archivo de configuración para Nginx:

```bash
sudo nano /etc/nginx/sites-available/mantenimiento
```

Con el siguiente contenido:

```nginx
server {
    listen 80;
    server_name tuejemplo.com www.tuejemplo.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/mantenimiento/mantenimiento.sock;
    }

    location /static {
        alias /var/www/mantenimiento/static;
    }
}
```

Habilita el sitio y recarga Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/mantenimiento /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Configuración de Seguridad

### 1. Configurar Firewall

```bash
# Instalar UFW si no está instalado
sudo apt install ufw

# Configurar reglas
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

### 2. Configurar HTTPS con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tuejemplo.com -d www.tuejemplo.com

# Configurar renovación automática
sudo systemctl status certbot.timer
```

## Monitoreo y Mantenimiento

### 1. Configurar Logs

Los logs de la aplicación estarán disponibles en:
- Nginx: `/var/log/nginx/error.log`
- Gunicorn: `sudo journalctl -u mantenimiento`

### 2. Tareas Programadas

Para tareas de mantenimiento periódicas, configura un cron job:

```bash
# Abrir el editor de crontab
crontab -e

# Agregar la siguiente línea para respaldos diarios
0 2 * * * pg_dump -U mantenimiento_user -d mantenimiento_db > /ruta/a/backups/mantenimiento_$(date +\%Y\%m\%d).sql
```

## Actualización de la Aplicación

Para actualizar la aplicación a una nueva versión:

```bash
cd /var/www/mantenimiento
source venv/bin/activate
git pull origin main
pip install -e ".[production]"
flask db upgrade
sudo systemctl restart mantenimiento
```

## Solución de Problemas

### La aplicación no se inicia

Verifica los logs de Gunicorn:
```bash
sudo journalctl -u mantenimiento -n 50 --no-pager
```

### Problemas de permisos

Asegúrate de que los permisos sean correctos:
```bash
sudo chown -R tu_usuario:www-data /var/www/mantenimiento
sudo chmod -R 775 /var/www/mantenimiento
```

### La base de datos no responde

Verifica el estado de PostgreSQL:
```bash
sudo systemctl status postgresql
```
