"""
Aplicación principal del sistema de gestión de mantenimiento.

Este módulo proporciona la interfaz web para el sistema de gestión de mantenimiento,
integrando los módulos de modelos, base de datos y utilidades.
"""

import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime

# Importar módulos propios
from mantenimiento.extensions import db_manager
from mantenimiento.utils.data_loader import DataLoader
from mantenimiento.utils.kpi_calculator import KPICalculator
from mantenimiento.models.activo import Activo
from mantenimiento.models.falla import Falla, EstadoFalla
from mantenimiento.models.orden_trabajo import OrdenTrabajo

# Configuración de la aplicación
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')

# Configuración de rutas
UPLOAD_FOLDER = 'uploads'
BACKUP_FOLDER = 'backups'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que existan los directorios necesarios
for folder in [UPLOAD_FOLDER, BACKUP_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

# Inicializar el gestor de base de datos
db_manager = DatabaseManager("mantenimiento.db")

def cargar_datos_iniciales():
    """Carga datos de ejemplo si la base de datos está vacía."""
    try:
        # Verificar si ya hay datos
        activos = db_manager.execute_query("SELECT COUNT(*) as count FROM activos")
        if activos and activos[0]['count'] == 0:
            # Cargar datos de ejemplo
            datos = DataLoader.cargar_datos_ejemplo("data/example")
            
            # Insertar datos en la base de datos
            for tipo, objetos in datos.items():
                DataLoader.insertar_en_bd(objetos, db_manager)
            
            print("Datos de ejemplo cargados correctamente.")
    except Exception as e:
        print(f"Error al cargar datos iniciales: {e}")

# Llamar a la función para cargar datos iniciales
cargar_datos_iniciales()

# Importar rutas después de la configuración para evitar importaciones circulares
from mantenimiento import routes

if __name__ == '__main__':
    # Crear tablas si no existen
    db_manager._create_tables()
    
    # Iniciar la aplicación
    app.run(debug=True)
