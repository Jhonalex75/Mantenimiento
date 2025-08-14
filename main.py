"""
Punto de entrada principal para la aplicación de gestión de mantenimiento.
"""
import os
import sys
from pathlib import Path

# Asegurarse de que el directorio raíz del proyecto esté en el PYTHONPATH
project_root = Path(__file__).parent.absolute()
src_path = project_root / 'src'

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Importar y crear la aplicación
from mantenimiento import create_app

if __name__ == '__main__':
    # Crear la aplicación
    app = create_app()
    
    # Iniciar la aplicación Flask
    print("Iniciando la aplicación de Gestión de Mantenimiento...")
    print(f"Modo debug: {'Activado' if app.debug else 'Desactivado'}")
    print(f"URL de la aplicación: http://{app.config.get('HOST', '127.0.0.1')}:{app.config.get('PORT', 5000)}")
    
    # Ejecutar la aplicación
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
