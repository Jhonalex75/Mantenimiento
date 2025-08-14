"""
Módulo para el manejo de la base de datos del sistema de mantenimiento.

Proporciona funciones para interactuar con la base de datos SQLite,
incluyendo la creación de tablas, inserción, actualización y consulta de datos.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Type, TypeVar, Callable, ClassVar
import logging
from datetime import datetime, date

# Importar modelos
from ..models.activo import Activo
from ..models.falla import Falla, EstadoFalla
from ..models.orden_trabajo import OrdenTrabajo, EstadoOrden, TipoOrden

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Clase para gestionar la conexión y operaciones con la base de datos."""
    
    def __init__(self, db_path: str = "mantenimiento.db"):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite.
        """
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Establece y devuelve una conexión a la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Crea las tablas necesarias si no existen."""
        sql_scripts = [
            """
            CREATE TABLE IF NOT EXISTS activos (
                activo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                criticidad TEXT NOT NULL,
                fecha_alta TEXT NOT NULL,
                ubicacion TEXT,
                responsable TEXT,
                estado TEXT DEFAULT 'Activo',
                horas_operacion REAL DEFAULT 0.0,
                ultimo_mantenimiento TEXT,
                proximo_mantenimiento TEXT,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS fallas (
                falla_id INTEGER PRIMARY KEY AUTOINCREMENT,
                activo_id INTEGER NOT NULL,
                fecha_reporte TEXT NOT NULL,
                fecha_cierre TEXT,
                descripcion TEXT NOT NULL,
                estado TEXT NOT NULL,
                tiempo_fuera_servicio_h REAL DEFAULT 0.0,
                causa_raiz TEXT,
                acciones_tomadas TEXT,
                costo_reparacion REAL,
                prioridad INTEGER DEFAULT 3,
                reportada_por TEXT NOT NULL,
                asignado_a TEXT,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (activo_id) REFERENCES activos (activo_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ordenes_trabajo (
                ot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                activo_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_programada TEXT NOT NULL,
                fecha_inicio TEXT,
                fecha_fin TEXT,
                estado TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                prioridad INTEGER DEFAULT 3,
                horas_estimadas REAL,
                horas_reales REAL,
                tecnico_asignado TEXT NOT NULL,
                observaciones TEXT,
                costo_estimado REAL,
                costo_real REAL,
                fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (activo_id) REFERENCES activos (activo_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS materiales_ot (
                material_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ot_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                cantidad REAL NOT NULL,
                unidad TEXT NOT NULL,
                costo_unitario REAL,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo (ot_id)
            )
            """
        ]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for script in sql_scripts:
                cursor.execute(script)
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Ejecuta una consulta SELECT y devuelve los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de filas resultantes
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error al ejecutar consulta: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una consulta de actualización (INSERT, UPDATE, DELETE).
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            ID de la fila insertada o número de filas afectadas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid or cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error al ejecutar actualización: {e}")
            conn.rollback()
            raise
    
    def insert_activo(self, activo_data: Dict[str, Any]) -> int:
        """
        Inserta un nuevo activo en la base de datos.
        
        Args:
            activo_data: Diccionario con los datos del activo
            
        Returns:
            ID del activo insertado
        """
        query = """
        INSERT INTO activos (
            nombre, criticidad, fecha_alta, ubicacion, 
            responsable, estado, horas_operacion, 
            ultimo_mantenimiento, proximo_mantenimiento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            activo_data['nombre'],
            activo_data['criticidad'],
            activo_data['fecha_alta'],
            activo_data.get('ubicacion'),
            activo_data.get('responsable'),
            activo_data.get('estado', 'Activo'),
            activo_data.get('horas_operacion', 0.0),
            activo_data.get('ultimo_mantenimiento'),
            activo_data.get('proximo_mantenimiento')
        )
        return self.execute_update(query, params)
    
    def get_activo(self, activo_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un activo por su ID.
        
        Args:
            activo_id: ID del activo a buscar
            
        Returns:
            Diccionario con los datos del activo o None si no se encuentra
        """
        query = "SELECT * FROM activos WHERE activo_id = ?"
        result = self.execute_query(query, (activo_id,))
        return dict(result[0]) if result else None
    
    def update_activo(self, activo_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un activo.
        
        Args:
            activo_id: ID del activo a actualizar
            update_data: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        if not update_data:
            return False
            
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        set_clause += ", fecha_actualizacion = CURRENT_TIMESTAMP"
        
        query = f"UPDATE activos SET {set_clause} WHERE activo_id = ?"
        params = list(update_data.values()) + [activo_id]
        
        try:
            rows_affected = self.execute_update(query, tuple(params))
            return rows_affected > 0
        except sqlite3.Error:
            return False
    
    def get_activos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de activos con filtros opcionales.
        
        Args:
            filtros: Diccionario con filtros a aplicar (ej: {'estado': 'Activo'})
            
        Returns:
            Lista de diccionarios con los datos de los activos
        """
        query = "SELECT * FROM activos"
        params = []
        
        if filtros:
            conditions = []
            for key, value in filtros.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY nombre"
        results = self.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    # Métodos similares para fallas y órdenes de trabajo...
    
    def backup_database(self, backup_dir: str = "backups") -> str:
        """
        Crea una copia de seguridad de la base de datos.
        
        Args:
            backup_dir: Directorio donde guardar la copia de seguridad
            
        Returns:
            Ruta al archivo de copia de seguridad creado
        """
        try:
            # Crear directorio de respaldo si no existe
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(backup_dir) / f"mantenimiento_backup_{timestamp}.db"
            
            # Crear copia de la base de datos
            with self._get_connection() as src_conn:
                with sqlite3.connect(backup_path) as dest_conn:
                    src_conn.backup(dest_conn)
            
            logger.info(f"Copia de seguridad creada en: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error al crear copia de seguridad: {e}")
            raise
