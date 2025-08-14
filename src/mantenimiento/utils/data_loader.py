"""
Módulo para cargar datos desde archivos CSV a la base de datos.

Este módulo proporciona funciones para cargar datos de ejemplo desde archivos CSV
a las tablas correspondientes en la base de datos.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Any, Union, ClassVar
import logging
from datetime import datetime
import pandas as pd

# Importar modelos
from ..models.activo import Activo
from ..models.falla import Falla, EstadoFalla
from ..models.orden_trabajo import OrdenTrabajo, EstadoOrden, TipoOrden

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class DataLoader:
    """Clase para cargar datos desde archivos CSV a la base de datos."""
    
    @staticmethod
    def cargar_desde_csv(
        archivo_csv: str, 
        modelo: Type[T], 
        mapeo_campos: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> List[T]:
        """
        Carga datos desde un archivo CSV y los convierte en objetos del modelo especificado.
        
        Args:
            archivo_csv: Ruta al archivo CSV
            modelo: Clase del modelo al que se convertirán los datos
            mapeo_campos: Diccionario que mapea nombres de columnas del CSV a campos del modelo
            **kwargs: Argumentos adicionales para pd.read_csv()
            
        Returns:
            Lista de objetos del modelo especificado
        """
        if not Path(archivo_csv).exists():
            logger.warning(f"El archivo {archivo_csv} no existe.")
            return []
        
        try:
            # Leer el archivo CSV con pandas
            df = pd.read_csv(archivo_csv, **kwargs)
            
            # Aplicar mapeo de campos si se proporciona
            if mapeo_campos:
                df = df.rename(columns=mapeo_campos)
            
            # Convertir a lista de diccionarios
            registros = df.to_dict('records')
            
            # Crear instancias del modelo
            objetos = []
            for registro in registros:
                try:
                    # Filtrar solo las claves que existen en el modelo
                    campos_validos = {
                        k: v for k, v in registro.items() 
                        if hasattr(modelo, k) or k in modelo.__annotations__
                    }
                    
                    # Crear instancia del modelo
                    objeto = modelo(**campos_validos)
                    objetos.append(objeto)
                except Exception as e:
                    logger.error(f"Error al crear instancia de {modelo.__name__}: {e}")
            
            logger.info(f"Cargados {len(objetos)} registros desde {archivo_csv}")
            return objetos
            
        except Exception as e:
            logger.error(f"Error al cargar datos desde {archivo_csv}: {e}")
            return []
    
    @classmethod
    def cargar_datos_ejemplo(
        cls, 
        directorio_datos: str = "data/example"
    ) -> Dict[str, List[Any]]:
        """
        Carga todos los archivos de ejemplo del directorio especificado.
        
        Args:
            directorio_datos: Directorio que contiene los archivos de ejemplo
            
        Returns:
            Diccionario con listas de objetos cargados, agrupados por tipo
        """
        from ..models import Activo, Falla, OrdenTrabajo
        
        # Mapeo de archivos a modelos y sus mapeos de campos
        configuracion_carga = {
            'activos.csv': {
                'modelo': Activo,
                'mapeo': {
                    'activo_id': 'activo_id',
                    'nombre': 'nombre',
                    'criticidad': 'criticidad',
                    'fecha_alta': 'fecha_alta',
                    'ubicacion': 'ubicacion',
                    'responsable': 'responsable',
                    'estado': 'estado',
                    'horas_operacion': 'horas_operacion',
                    'ultimo_mantenimiento': 'ultimo_mantenimiento',
                    'proximo_mantenimiento': 'proximo_mantenimiento'
                }
            },
            'fallas.csv': {
                'modelo': Falla,
                'mapeo': {
                    'falla_id': 'falla_id',
                    'activo_id': 'activo_id',
                    'fecha_reporte': 'fecha_reporte',
                    'fecha_cierre': 'fecha_cierre',
                    'descripcion': 'descripcion',
                    'estado': 'estado',
                    'tiempo_fuera_servicio_h': 'tiempo_fuera_servicio_h',
                    'causa_raiz': 'causa_raiz',
                    'acciones_tomadas': 'acciones_tomadas',
                    'costo_reparacion': 'costo_reparacion',
                    'prioridad': 'prioridad',
                    'reportada_por': 'reportada_por',
                    'asignado_a': 'asignado_a'
                }
            },
            'ordenes_trabajo.csv': {
                'modelo': OrdenTrabajo,
                'mapeo': {
                    'ot_id': 'ot_id',
                    'activo_id': 'activo_id',
                    'tipo': 'tipo',
                    'fecha_creacion': 'fecha_creacion',
                    'fecha_programada': 'fecha_programada',
                    'fecha_inicio': 'fecha_inicio',
                    'fecha_fin': 'fecha_fin',
                    'estado': 'estado',
                    'descripcion': 'descripcion',
                    'prioridad': 'prioridad',
                    'horas_estimadas': 'horas_estimadas',
                    'horas_reales': 'horas_reales',
                    'tecnico_asignado': 'tecnico_asignado',
                    'observaciones': 'observaciones',
                    'costo_estimado': 'costo_estimado',
                    'costo_real': 'costo_real'
                }
            }
        }
        
        resultados = {}
        
        for archivo, config in configuracion_carga.items():
            ruta_archivo = Path(directorio_datos) / archivo
            
            if not ruta_archivo.exists():
                logger.warning(f"Archivo no encontrado: {ruta_archivo}")
                continue
            
            # Cargar datos del archivo
            objetos = cls.cargar_desde_csv(
                archivo_csv=str(ruta_archivo),
                modelo=config['modelo'],
                mapeo_campos=config['mapeo'],
                parse_dates=True,
                infer_datetime_format=True
            )
            
            # Almacenar resultados
            nombre_modelo = config['modelo'].__name__.lower() + 's'
            resultados[nombre_modelo] = objetos
        
        return resultados
    
    @staticmethod
    def insertar_en_bd(objetos: List[Any], db_manager) -> Dict[str, int]:
        """
        Inserta una lista de objetos en la base de datos.
        
        Args:
            objetos: Lista de objetos a insertar
            db_manager: Instancia de DatabaseManager
            
        Returns:
            Diccionario con estadísticas de la operación
        """
        if not objetos:
            return {'total': 0, 'exitosos': 0, 'fallidos': 0}
        
        exitosos = 0
        fallidos = 0
        
        for obj in objetos:
            try:
                # Convertir el objeto a diccionario
                datos = obj.to_dict()
                
                # Insertar en la base de datos
                if hasattr(obj, 'activo_id') and obj.activo_id:
                    # Actualizar si ya existe
                    db_manager.actualizar_activo(obj.activo_id, datos)
                else:
                    # Insertar nuevo
                    if isinstance(obj, Activo):
                        db_manager.insert_activo(datos)
                    # Agregar otros tipos de inserción según sea necesario
                
                exitosos += 1
            except Exception as e:
                logger.error(f"Error al insertar objeto en la base de datos: {e}")
                fallidos += 1
        
        return {
            'total': len(objetos),
            'exitosos': exitosos,
            'fallidos': fallidos
        }
