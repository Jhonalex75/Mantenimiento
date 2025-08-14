"""
Módulo para almacenar instancias compartidas y evitar importaciones circulares.
"""
import os
from pathlib import Path

# Importar DatabaseManager con una ruta absoluta para evitar problemas de importación
from mantenimiento.utils.database import DatabaseManager

# Obtener la ruta al directorio del paquete
package_dir = Path(os.path.dirname(os.path.abspath(__file__)))

# Construir la ruta a la base de datos relativa al paquete
db_path = str(package_dir.parent.parent / 'mantenimiento.db')

# Crear instancia del gestor de base de datos
db_manager = DatabaseManager(db_path)
