# Guía de Desarrollo

Bienvenido a la guía de desarrollo del Sistema de Gestión de Mantenimiento. Este documento proporciona información para desarrolladores que deseen contribuir al proyecto o entender su funcionamiento interno.

## Estructura del Proyecto

```
src/
├── mantenimiento/
│   ├── __init__.py     # Inicialización de la aplicación
│   ├── app.py          # Configuración de la aplicación
│   ├── models/         # Modelos de datos
│   ├── routes/         # Blueprints de rutas
│   ├── services/       # Lógica de negocio
│   ├── utils/          # Utilidades y helpers
│   └── static/         # Archivos estáticos
```

## Configuración del Entorno de Desarrollo

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/mantenimiento.git
   cd mantenimiento
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Instalar dependencias de desarrollo**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Configurar pre-commit**
   ```bash
   pre-commit install
   ```

## Convenciones de Código

### Estilo de Código

- Seguimos las convenciones de estilo de código de [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usamos `black` para formateo de código
- Usamos `isort` para ordenar importaciones
- Usamos `flake8` para verificación de estilo

### Convenciones de Git

- Usamos [Conventional Commits](https://www.conventionalcommits.org/)
- Las ramas de características siguen el formato: `feature/nombre-de-la-caracteristica`
- Las ramas de corrección siguen el formato: `fix/descripcion-del-fix`

## Pruebas

El proyecto incluye pruebas unitarias y de integración. Para ejecutarlas:

```bash
pytest
```

Para ver la cobertura de código:

```bash
pytest --cov=src
```

## Documentación

La documentación se genera usando MkDocs. Para verla localmente:

```bash
mkdocs serve
```

## Proceso de Pull Request

1. Crea una rama para tu característica o corrección
2. Realiza tus cambios siguiendo las convenciones
3. Asegúrate de que todas las pruebas pasen
4. Actualiza la documentación según sea necesario
5. Envía un Pull Request con una descripción clara de los cambios

## Estándares de Código

- Escribe docstrings siguiendo el formato Google Style
- Documenta todas las funciones y clases públicas
- Incluye ejemplos en la documentación cuando sea apropiado
- Mantén las funciones pequeñas y enfocadas en una sola responsabilidad

## Depuración

Para depurar la aplicación en desarrollo, puedes usar el modo debug de Flask:

```bash
export FLASK_DEBUG=1  # En Linux/macOS
set FLASK_DEBUG=1     # En Windows
flask run
```

## Construyendo para Producción

Para crear una versión lista para producción:

```bash
python setup.py sdist bdist_wheel
```

## Seguridad

- Nunca expongas información sensible en el código
- Usa variables de entorno para configuraciones sensibles
- Sigue las mejores prácticas de seguridad de OWASP

## Rendimiento

- Usa consultas eficientes a la base de datos
- Implementa caché donde sea apropiado
- Monitorea el rendimiento en producción
