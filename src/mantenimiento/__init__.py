"""
Paquete principal de la aplicación de Gestión de Mantenimiento.

Este paquete contiene los módulos principales de la aplicación:
- models: Modelos de datos (Activo, Falla, OrdenTrabajo)
- utils: Utilidades (base de datos, carga de datos, cálculos)
- templates: Plantillas HTML
- static: Archivos estáticos (CSS, JS, imágenes)
"""

import os

# Importar la función de fábrica de la aplicación
from .factory import create_app

# Crear la aplicación por defecto para facilitar la importación
app = create_app()

# Importar y configurar extensiones
try:
    from .extensions import db_manager
    
    # Importar modelos
    from .models.activo import Activo
    from .models.falla import Falla, EstadoFalla
    from .models.orden_trabajo import OrdenTrabajo, EstadoOrden, TipoOrden
    
    # Importar utilidades
    from .utils.data_loader import DataLoader
    from .utils.kpi_calculator import KPICalculator
    
    # Importar rutas después de la configuración para evitar importaciones circulares
    from . import routes
    
    # Configuración de la aplicación
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-123'),
        UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload size
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Asegurarse de que exista el directorio de subidas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
except ImportError as e:
    print(f"Error al importar módulos: {e}")

__version__ = '0.1.0'

# Lista de símbolos que se exportan cuando se usa 'from mantenimiento import *'
__all__ = [
    'app',
    'db_manager',
    'Activo',
    'Falla',
    'EstadoFalla',
    'OrdenTrabajo',
    'EstadoOrden',
    'TipoOrden',
    'DataLoader',
    'KPICalculator'
]
