"""
Módulo de modelos de datos para el sistema de mantenimiento.

Contiene las definiciones de clases para:
- Activo: Equipos y activos a mantener
- Falla: Registro de fallas reportadas
- OrdenTrabajo: Órdenes de trabajo generadas
"""

from .activo import Activo
from .falla import Falla
from .orden_trabajo import OrdenTrabajo

__all__ = ['Activo', 'Falla', 'OrdenTrabajo']
