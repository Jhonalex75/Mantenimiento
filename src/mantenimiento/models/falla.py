from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, ClassVar, Union
from enum import Enum

class EstadoFalla(str, Enum):
    REPORTADA = "Reportada"
    EN_REVISION = "En Revisión"
    EN_REPARACION = "En Reparación"
    RESUELTA = "Resuelta"
    CERRADA = "Cerrada"
    INVALIDA = "Inválida"

@dataclass
class Falla:
    """
    Clase que representa una falla reportada en el sistema de mantenimiento.
    
    Atributos:
        falla_id: Identificador único de la falla
        activo_id: ID del activo relacionado
        fecha_reporte: Fecha y hora del reporte de la falla
        fecha_cierre: Fecha y hora de cierre de la falla (opcional)
        descripcion: Descripción detallada de la falla
        estado: Estado actual de la falla (ver clase EstadoFalla)
        tiempo_fuera_servicio_h: Tiempo total que el activo estuvo fuera de servicio (horas)
        causa_raiz: Causa raíz identificada (opcional)
        acciones_tomadas: Acciones realizadas para solucionar la falla
        costo_reparacion: Costo estimado de la reparación (opcional)
        prioridad: Nivel de prioridad (1-5, siendo 1 la más alta)
        reportada_por: Persona que reportó la falla
        asignado_a: Técnico asignado para atender la falla (opcional)
    """
    falla_id: int
    activo_id: int
    fecha_reporte: str
    descripcion: str
    reportada_por: str
    
    # Atributos opcionales
    fecha_cierre: Optional[str] = None
    estado: EstadoFalla = EstadoFalla.REPORTADA
    tiempo_fuera_servicio_h: float = 0.0
    causa_raiz: Optional[str] = None
    acciones_tomadas: str = ""
    costo_reparacion: Optional[float] = None
    prioridad: int = 3
    asignado_a: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Falla a un diccionario."""
        return {
            "falla_id": self.falla_id,
            "activo_id": self.activo_id,
            "fecha_reporte": self.fecha_reporte,
            "fecha_cierre": self.fecha_cierre,
            "descripcion": self.descripcion,
            "estado": self.estado.value,
            "tiempo_fuera_servicio_h": self.tiempo_fuera_servicio_h,
            "causa_raiz": self.causa_raiz,
            "acciones_tomadas": self.acciones_tomadas,
            "costo_reparacion": self.costo_reparacion,
            "prioridad": self.prioridad,
            "reportada_por": self.reportada_por,
            "asignado_a": self.asignado_a
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Falla':
        """Crea una instancia de Falla a partir de un diccionario."""
        # Convertir el estado de string a Enum si es necesario
        if isinstance(data.get('estado'), str):
            data['estado'] = EstadoFalla(data['estado'])
        return cls(**data)
    
    def actualizar_estado(self, nuevo_estado: EstadoFalla) -> None:
        """Actualiza el estado de la falla."""
        self.estado = nuevo_estado
        
        # Si se marca como resuelta o cerrada, registrar la fecha de cierre
        if nuevo_estado in [EstadoFalla.RESUELTA, EstadoFalla.CERRADA] and not self.fecha_cierre:
            self.fecha_cierre = datetime.now().isoformat()
    
    def asignar_tecnico(self, nombre_tecnico: str) -> None:
        """Asigna un técnico para atender la falla."""
        self.asignado_a = nombre_tecnico
        if self.estado == EstadoFalla.REPORTADA:
            self.estado = EstadoFalla.EN_REVISION
    
    def registrar_accion(self, accion: str) -> None:
        """Registra una acción tomada para solucionar la falla."""
        if self.acciones_tomadas:
            self.acciones_tomadas += "\n" + accion
        else:
            self.acciones_tomadas = accion
