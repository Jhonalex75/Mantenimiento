from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, ClassVar
from enum import Enum

class TipoOrden(str, Enum):
    PREVENTIVO = "Preventivo"
    CORRECTIVO = "Correctivo"
    PREDICTIVO = "Predictivo"
    INSPECCION = "Inspección"
    CALIBRACION = "Calibración"
    OTRO = "Otro"

class EstadoOrden(str, Enum):
    PENDIENTE = "Pendiente"
    PROGRAMADA = "Programada"
    EN_PROCESO = "En Proceso"
    PAUSADA = "Pausada"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"

@dataclass
class OrdenTrabajo:
    """
    Clase que representa una orden de trabajo en el sistema de mantenimiento.
    
    Atributos:
        ot_id: Identificador único de la orden de trabajo
        activo_id: ID del activo relacionado
        tipo: Tipo de orden (Preventivo, Correctivo, etc.)
        fecha_creacion: Fecha de creación de la orden
        fecha_programada: Fecha programada para la ejecución
        fecha_inicio: Fecha real de inicio (opcional)
        fecha_fin: Fecha real de finalización (opcional)
        estado: Estado actual de la orden
        descripcion: Descripción detallada del trabajo a realizar
        prioridad: Nivel de prioridad (1-5, siendo 1 la más alta)
        horas_estimadas: Horas estimadas para completar el trabajo
        horas_reales: Horas reales tomadas (opcional)
        tecnico_asignado: Nombre del técnico asignado
        materiales: Lista de materiales necesarios (opcional)
        observaciones: Observaciones adicionales (opcional)
        costo_estimado: Costo estimado de la orden (opcional)
        costo_real: Costo real de la orden (opcional)
    """
    ot_id: int
    activo_id: int
    tipo: TipoOrden
    fecha_creacion: str
    fecha_programada: str
    descripcion: str
    tecnico_asignado: str
    
    # Atributos opcionales
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    estado: EstadoOrden = EstadoOrden.PENDIENTE
    prioridad: int = 3
    horas_estimadas: float = 1.0
    horas_reales: Optional[float] = None
    materiales: List[Dict[str, Union[str, float]]] = None
    observaciones: str = ""
    costo_estimado: Optional[float] = None
    costo_real: Optional[float] = None
    
    def __post_init__(self):
        if self.materiales is None:
            self.materiales = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto OrdenTrabajo a un diccionario."""
        return {
            "ot_id": self.ot_id,
            "activo_id": self.activo_id,
            "tipo": self.tipo.value,
            "fecha_creacion": self.fecha_creacion,
            "fecha_programada": self.fecha_programada,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "estado": self.estado.value,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad,
            "horas_estimadas": self.horas_estimadas,
            "horas_reales": self.horas_reales,
            "tecnico_asignado": self.tecnico_asignado,
            "materiales": self.materiales,
            "observaciones": self.observaciones,
            "costo_estimado": self.costo_estimado,
            "costo_real": self.costo_real
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrdenTrabajo':
        """Crea una instancia de OrdenTrabajo a partir de un diccionario."""
        # Convertir los enums de string a sus respectivas clases
        if isinstance(data.get('tipo'), str):
            data['tipo'] = TipoOrden(data['tipo'])
        if isinstance(data.get('estado'), str):
            data['estado'] = EstadoOrden(data['estado'])
        return cls(**data)
    
    def iniciar_trabajo(self) -> None:
        """Marca la orden como en proceso y registra la hora de inicio."""
        if self.estado == EstadoOrden.PENDIENTE or self.estado == EstadoOrden.PROGRAMADA:
            self.estado = EstadoOrden.EN_PROCESO
            if not self.fecha_inicio:
                self.fecha_inicio = datetime.now().isoformat()
    
    def pausar_trabajo(self) -> None:
        """Pausa una orden de trabajo en proceso."""
        if self.estado == EstadoOrden.EN_PROCESO:
            self.estado = EstadoOrden.PAUSADA
    
    def reanudar_trabajo(self) -> None:
        """Reanuda una orden de trabajo pausada."""
        if self.estado == EstadoOrden.PAUSADA:
            self.estado = EstadoOrden.EN_PROCESO
    
    def completar_trabajo(self, observaciones: str = "", horas_reales: Optional[float] = None, 
                         costo_real: Optional[float] = None) -> None:
        """Marca la orden como completada y registra la hora de finalización."""
        self.estado = EstadoOrden.COMPLETADA
        self.fecha_fin = datetime.now().isoformat()
        self.observaciones = observaciones
        
        if horas_reales is not None:
            self.horas_reales = horas_reales
        if costo_real is not None:
            self.costo_real = costo_real
    
    def agregar_material(self, nombre: str, cantidad: float, unidad: str, 
                        costo_unitario: Optional[float] = None) -> None:
        """Agrega un material a la lista de materiales necesarios."""
        material = {
            "nombre": nombre,
            "cantidad": cantidad,
            "unidad": unidad,
            "costo_unitario": costo_unitario
        }
        self.materiales.append(material)
        
        # Actualizar costo estimado si se proporcionó el costo unitario
        if costo_unitario is not None:
            if self.costo_estimado is None:
                self.costo_estimado = 0.0
            self.costo_estimado += cantidad * costo_unitario
