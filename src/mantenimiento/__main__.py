"""
Punto de entrada principal para la aplicación de gestión de mantenimiento.

Este módulo permite ejecutar la aplicación directamente con:
    python -m mantenimiento
"""

from .app import app, db_manager

if __name__ == '__main__':
    # Crear tablas si no existen
    db_manager._create_tables()
    
    # Iniciar la aplicación
    app.run(debug=True)
