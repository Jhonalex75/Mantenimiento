# Sistema de Gestión de Mantenimiento

Aplicación web para la gestión de mantenimiento de activos, registro de fallas, órdenes de trabajo y cálculo de KPIs (MTBF, MTTR, Disponibilidad).

## Características

- **Gestión de Activos**: Registro y seguimiento detallado de equipos y maquinaria
- **Sistema de Fallas**: Reporte y seguimiento de fallas con estados personalizables
- **Órdenes de Trabajo**: Creación, asignación y seguimiento de tareas de mantenimiento
- **Métricas Avanzadas**: Cálculo automático de KPIs (MTBF, MTTR, Disponibilidad)
- **Interfaz Moderna**: Diseño responsivo con Bootstrap 5
- **API RESTful**: Endpoints para integración con otros sistemas
- **Autenticación**: Sistema de usuarios y roles
- **Exportación de Datos**: Generación de informes en múltiples formatos

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para control de versiones)

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Jhonalex75/mantenimiento.git
   cd mantenimiento
   ```

2. **Crear y activar un entorno virtual (recomendado)**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   
   # Linux/MacOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -e .
   ```

## Estructura del proyecto

```
mantenimiento/
├── data/                   # Datos de ejemplo
│   ├── activos.csv
│   ├── fallas.csv
│   └── ordenes_trabajo.csv
├── src/
│   └── mantenimiento/     # Código fuente del paquete
│       ├── __init__.py    # Inicialización del paquete
│       ├── app.py         # Aplicación Flask principal
│       ├── routes.py      # Rutas de la aplicación
│       ├── models/        # Modelos de datos
│       │   ├── __init__.py
│       │   ├── activo.py
│       │   ├── falla.py
│       │   └── orden_trabajo.py
│       └── utils/         # Utilidades
│           ├── __init__.py
│           ├── database.py
│           ├── data_loader.py
│           └── kpi_calculator.py
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── activos/
│   ├── fallas/
│   └── ordenes/
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── uploads/              # Archivos subidos por los usuarios
├── backups/              # Copias de seguridad
├── setup.py              # Configuración del paquete
└── README.md             # Este archivo
```

## Uso

### Iniciar la aplicación

```bash
# Desde el directorio raíz del proyecto
python -m mantenimiento
```

La aplicación estará disponible en `http://127.0.0.1:5000/`

### Cargar datos de ejemplo

1. Inicia la aplicación
2. Navega a la sección de configuración
3. Haz clic en "Cargar datos de ejemplo"

### Acceso a la aplicación

- **URL local**: `http://127.0.0.1:5000/`
- **Usuario por defecto**: admin
- **Contraseña por defecto**: admin123

## KPIs

La aplicación calcula automáticamente los siguientes KPIs:

- **MTBF** (Mean Time Between Failures): Tiempo medio entre fallas
- **MTTR** (Mean Time To Repair): Tiempo medio para reparar
- **Disponibilidad**: \( A = \dfrac{MTBF}{MTBF + MTTR} \)

## Flujo de Trabajo con Git

### Para contribuir al proyecto:

1. **Haz un fork** del repositorio
2. **Clona tu fork** localmente:
   ```bash
   git clone https://github.com/tu-usuario/mantenimiento.git
   cd mantenimiento
   ```

3. **Configura el repositorio remoto**:
   ```bash
   git remote add upstream https://github.com/Jhonalex75/mantenimiento.git
   ```

4. **Crea una rama** para tu característica o corrección:
   ```bash
   git checkout -b nombre-de-tu-rama
   ```

5. **Haz commit** de tus cambios con mensajes descriptivos:
   ```bash
   git add .
   git commit -m "feat: Añade nueva funcionalidad"
   ```

6. **Sincroniza** con el repositorio principal:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

7. **Sube** tus cambios a tu fork:
   ```bash
   git push origin nombre-de-tu-rama
   ```

8. **Abre un Pull Request** en GitHub

### Convención de Commits

- `feat:` Nueva característica
- `fix:` Corrección de errores
- `docs:` Cambios en la documentación
- `style:` Cambios de formato (puntos y comas, indentación, etc.)
- `refactor:` Cambios que no corrigen errores ni agregan funcionalidades
- `test:` Añadir o modificar pruebas
- `chore:` Cambios en el proceso de construcción o herramientas auxiliares

## Estructura del Código

La aplicación sigue la estructura de paquetes de Python con el patrón Factory de Flask:

- `src/mantenimiento/` - Paquete principal
  - `__init__.py` - Fábrica de la aplicación
  - `app.py` - Configuración de la aplicación
  - `routes/` - Módulos de rutas (blueprints)
  - `models/` - Modelos de datos
  - `utils/` - Utilidades y lógica de negocio
  - `static/` - Archivos estáticos
  - `templates/` - Plantillas HTML

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contribución

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Revisa los issues abiertos o crea uno nuevo
2. Haz fork del repositorio
3. Crea una rama con tu característica o corrección
4. Asegúrate de que los tests pasen
5. Envía un Pull Request con una descripción clara

## Contacto

- **Autor**: Jhonalex75
- **Correo**: tu@email.com
- **GitHub**: [Jhonalex75](https://github.com/Jhonalex75)

mttr = fallas.groupby("activo_id")["tiempo_fuera_servicio_h"].mean()

def disponibilidad(mtbf_h, mttr_h):
    return mtbf_h/(mtbf_h+mttr_h)

res = pd.DataFrame({"MTBF_h": mtbf, "MTTR_h": mttr}).dropna()
res["A"] = disponibilidad(res["MTBF_h"], res["MTTR_h"])
print(res)
```

## Planificación preventiva
- Define periodicidades (p.ej., 250 h cambio de aceite, 1000 h inspección mayor).
- Genera OTs preventivas y monitorea cumplimiento (on-time vs overdue).

## Visualización
- Histogramas de MTBF/MTTR por activo.
- Tendencias de OTs por mes, tasa de fallas.

## Pruebas sugeridas
- Datos sintéticos reproducibles para validar KPIs.
- Cohesión entre `ordenes_trabajo` y `fallas` (integridad referencial).

## Roadmap
- Clasificación de criticidad y priorización automática.
- Dashboards (Streamlit/Plotly) para KPIs.
- Exportación a Excel/CSV con reportes mensuales.

## Licencia
MIT (o la del repositorio donde se utilice).
