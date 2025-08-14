"""
Módulo para el cálculo de KPIs de mantenimiento.

Este módulo proporciona funciones para calcular métricas clave de mantenimiento como:
- MTBF (Mean Time Between Failures)
- MTTR (Mean Time To Repair)
- Disponibilidad
- Cumplimiento del plan de mantenimiento
- Costos de mantenimiento
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, ClassVar
import numpy as np
import pandas as pd
from ..models.activo import Activo
from ..models.falla import Falla, EstadoFalla
from ..models.orden_trabajo import OrdenTrabajo, EstadoOrden, TipoOrden

class KPICalculator:
    """Clase para calcular métricas clave de mantenimiento."""
    
    @staticmethod
    def calcular_mtbf(fechas_fallas: List[datetime]) -> Tuple[float, int]:
        """
        Calcula el MTBF (Mean Time Between Failures) en horas.
        
        Args:
            fechas_fallas: Lista de fechas de fallas ordenadas de más antigua a más reciente
            
        Returns:
            Tupla con (MTBF en horas, número de intervalos)
        """
        if len(fechas_fallas) < 2:
            return 0.0, 0
            
        # Ordenar fechas por si acaso no vienen ordenadas
        fechas_ordenadas = sorted(fechas_fallas)
        
        # Calcular diferencias entre fallas consecutivas (en segundos)
        diferencias = []
        for i in range(1, len(fechas_ordenadas)):
            delta = fechas_ordenadas[i] - fechas_ordenadas[i-1]
            diferencias.append(delta.total_seconds() / 3600)  # Convertir a horas
        
        if not diferencias:
            return 0.0, 0
            
        mtbf = sum(diferencias) / len(diferencias)
        return mtbf, len(diferencias)
    
    @staticmethod
    def calcular_mttr(tiempos_reparacion: List[float]) -> float:
        """
        Calcula el MTTR (Mean Time To Repair) en horas.
        
        Args:
            tiempos_reparacion: Lista de tiempos de reparación en horas
            
        Returns:
            MTTR en horas
        """
        if not tiempos_reparacion:
            return 0.0
            
        return sum(tiempos_reparacion) / len(tiempos_reparacion)
    
    @staticmethod
    def calcular_disponibilidad(mtbf: float, mttr: float) -> float:
        """
        Calcula la disponibilidad del equipo.
        
        Fórmula: Disponibilidad = MTBF / (MTBF + MTTR)
        
        Args:
            mtbf: MTBF en horas
            mttr: MTTR en horas
            
        Returns:
            Disponibilidad como valor entre 0 y 1 (donde 1 = 100% disponible)
        """
        if mtbf <= 0:
            return 0.0
            
        return mtbf / (mtbf + mttr)
    
    @classmethod
    def calcular_kpis_activo(
        cls, 
        fallas: List[Dict[str, Any]], 
        ordenes_trabajo: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calcula los KPIs principales para un activo.
        
        Args:
            fallas: Lista de fallas del activo
            ordenes_trabajo: Lista de órdenes de trabajo del activo (opcional)
            
        Returns:
            Diccionario con los KPIs calculados
        """
        # Filtrar solo fallas resueltas/cerradas para MTBF/MTTR
        fallas_resueltas = [
            f for f in fallas 
            if f.get('estado') in ['Resuelta', 'Cerrada', 'COMPLETADA']
        ]
        
        # Calcular MTBF
        fechas_fallas = [
            datetime.fromisoformat(f['fecha_reporte']) 
            for f in fallas_resueltas
            if 'fecha_reporte' in f
        ]
        mtbf, num_intervalos = cls.calcular_mtbf(fechas_fallas)
        
        # Calcular MTTR
        tiempos_reparacion = [
            f.get('tiempo_fuera_servicio_h', 0) 
            for f in fallas_resueltas
            if 'tiempo_fuera_servicio_h' in f and f.get('tiempo_fuera_servicio_h') is not None
        ]
        mttr = cls.calcular_mttr(tiempos_reparacion) if tiempos_reparacion else 0.0
        
        # Calcular disponibilidad
        disponibilidad = cls.calcular_disponibilidad(mtbf, mttr) if mtbf > 0 else 1.0
        
        # Calcular cumplimiento de mantenimiento preventivo (si hay datos)
        cumplimiento_preventivo = None
        if ordenes_trabajo:
            preventivos = [
                ot for ot in ordenes_trabajo 
                if ot.get('tipo') in ['Preventivo', 'PREVENTIVO', 'preventivo']
            ]
            
            if preventivos:
                completados_a_tiempo = sum(
                    1 for ot in preventivos 
                    if ot.get('estado') in ['Completada', 'COMPLETADA'] and
                       ot.get('fecha_fin') and 
                       ot.get('fecha_programada') and
                       datetime.fromisoformat(ot['fecha_fin']) <= 
                       datetime.fromisoformat(ot['fecha_programada']) + timedelta(days=1)
                )
                
                if preventivos:
                    cumplimiento_preventivo = (completados_a_tiempo / len(preventivos)) * 100
        
        # Calcular costos (si hay datos)
        costo_total = 0.0
        if ordenes_trabajo:
            costo_total = sum(
                ot.get('costo_real', 0) or 0 
                for ot in ordenes_trabajo 
                if ot.get('costo_real') is not None
            )
        
        return {
            'mtbf_horas': mtbf,
            'mttr_horas': mttr,
            'disponibilidad': disponibilidad,
            'num_fallas': len(fallas_resueltas),
            'num_intervalos_mtbf': num_intervalos,
            'cumplimiento_preventivo': cumplimiento_preventivo,
            'costo_total_mantenimiento': costo_total,
            'ultima_actualizacion': datetime.now().isoformat()
        }
    
    @staticmethod
    def generar_reporte_estadistico(
        fallas: List[Dict[str, Any]], 
        periodo_inicio: Optional[datetime] = None,
        periodo_fin: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte estadístico de las fallas en un período determinado.
        
        Args:
            fallas: Lista de fallas a analizar
            periodo_inicio: Fecha de inicio del período (opcional)
            periodo_fin: Fecha de fin del período (opcional)
            
        Returns:
            Diccionario con estadísticas de fallas
        """
        if not fallas:
            return {}
            
        # Filtrar por período si se especifica
        if periodo_inicio or periodo_fin:
            fallas_filtradas = []
            for falla in fallas:
                if 'fecha_reporte' not in falla:
                    continue
                    
                try:
                    fecha_falla = datetime.fromisoformat(falla['fecha_reporte'])
                    if (periodo_inicio and fecha_falla < periodo_inicio) or \
                       (periodo_fin and fecha_falla > periodo_fin):
                        continue
                    fallas_filtradas.append(falla)
                except (ValueError, TypeError):
                    continue
        else:
            fallas_filtradas = fallas
        
        if not fallas_filtradas:
            return {}
        
        # Calcular estadísticas básicas
        tiempos_reparacion = [
            f.get('tiempo_fuera_servicio_h', 0) 
            for f in fallas_filtradas 
            if f.get('tiempo_fuera_servicio_h') is not None
        ]
        
        num_fallas = len(fallas_filtradas)
        costos_reparacion = [
            f.get('costo_reparacion', 0) 
            for f in fallas_filtradas 
            if f.get('costo_reparacion') is not None
        ]
        
        # Agrupar por causa raíz (si existe el campo)
        causas_raiz = {}
        for falla in fallas_filtradas:
            causa = falla.get('causa_raiz', 'No especificada')
            causas_raiz[causa] = causas_raiz.get(causa, 0) + 1
        
        # Ordenar causas por frecuencia
        causas_ordenadas = sorted(
            causas_raiz.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            'periodo_inicio': periodo_inicio.isoformat() if periodo_inicio else None,
            'periodo_fin': periodo_fin.isoformat() if periodo_fin else None,
            'total_fallas': num_fallas,
            'tiempo_promedio_reparacion': np.mean(tiempos_reparacion) if tiempos_reparacion else 0,
            'tiempo_total_fuera_servicio': sum(tiempos_reparacion),
            'costo_total_reparaciones': sum(costos_reparacion) if costos_reparacion else 0,
            'causas_raiz': dict(causas_ordenadas[:5]),  # Top 5 causas
            'distribucion_por_estado': dict(pd.Series([f.get('estado', 'Desconocido') for f in fallas_filtradas]).value_counts().head())
        }
