"""
Módulo de fábrica de la aplicación Flask.

Este módulo proporciona una función para crear y configurar la aplicación Flask.
"""
import os
from pathlib import Path
from flask import Flask
from .utils.database import DatabaseManager


def create_app(test_config=None):
    """Crea y configura la aplicación Flask.
    
    Args:
        test_config: Configuración para pruebas (opcional).
        
    Returns:
        Flask: La aplicación Flask configurada.
    """
    # Crear la instancia de la aplicación
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración predeterminada
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-123'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload size
        DATABASE=os.path.join(app.instance_path, 'mantenimiento.db'),
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Aplicar configuración de prueba si se proporciona
    if test_config is None:
        # Cargar la configuración de instancia si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Cargar la configuración de prueba
        app.config.update(test_config)
    
    # Asegurarse de que exista la carpeta de instancia
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError as e:
        print(f"Error al crear directorios: {e}")
    
    # Inicializar la base de datos
    db_manager = DatabaseManager(app.config['DATABASE'])
    db_manager._create_tables()
    
    # Registrar blueprints
    from . import routes
    app.register_blueprint(routes.bp)
    
    # Hacer que el gestor de base de datos esté disponible en el contexto de la aplicación
    app.db_manager = db_manager
    
    return app
