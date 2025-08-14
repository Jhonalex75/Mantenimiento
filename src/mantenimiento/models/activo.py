from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, ClassVar

@dataclass
class Activo:
    """
    Clase que representa un activo o equipo en el sistema de mantenimiento.
    
    Atributos:
        activo_id: Identificador único del activo
        nombre: Nombre descriptivo del activo
        criticidad: Nivel de criticidad (Alta, Media, Baja)
        fecha_alta: Fecha de registro del activo en el sistema
        ubicacion: Ubicación física del activo
        responsable: Persona a cargo del activo
        estado: Estado actual del activo (Activo, Inactivo, En Mantenimiento, etc.)
        horas_operacion: Horas acumuladas de operación (opcional)
        ultimo_mantenimiento: Fecha del último mantenimiento (opcional)
        proximo_mantenimiento: Fecha del próximo mantenimiento programado (opcional)
    """
    activo_id: int
    nombre: str
    criticidad: str
    fecha_alta: str
    ubicacion: str
    responsable: str
    estado: str = "Activo"
    horas_operacion: float = 0.0
    ultimo_mantenimiento: Optional[str] = None
    proximo_mantenimiento: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Activo a un diccionario."""
        return {
            "activo_id": self.activo_id,
            "nombre": self.nombre,
            "criticidad": self.criticidad,
            "fecha_alta": self.fecha_alta,
            "ubicacion": self.ubicacion,
            "responsable": self.responsable,
            "estado": self.estado,
            "horas_operacion": self.horas_operacion,
            "ultimo_mantenimiento": self.ultimo_mantenimiento,
            "proximo_mantenimiento": self.proximo_mantenimiento
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activo':
        """Crea una instancia de Activo a partir de un diccionario."""
        return cls(**data)
    
    def actualizar_estado(self, nuevo_estado: str) -> None:
        """Actualiza el estado del activo."""
        self.estado = nuevo_estado
    
    def programar_mantenimiento(self, fecha_programada: str) -> None:
        """Programa el próximo mantenimiento para el activo."""
        self.proximo_mantenimiento = fecha_programada
