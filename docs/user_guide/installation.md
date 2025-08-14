# Guía de Instalación

Esta guía te ayudará a instalar el Sistema de Gestión de Mantenimiento en tu entorno local.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, solo si vas a clonar el repositorio)

## Instalación en Windows

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/mantenimiento.git
cd mantenimiento
```

### 2. Crear un Entorno Virtual (Recomendado)

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual
.\\.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -e .
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
FLASK_APP=mantenimiento
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URI=sqlite:///mantenimiento.db
```

### 5. Inicializar la Base de Datos

```bash
flask init-db
```

### 6. Ejecutar la Aplicación

```bash
flask run
```

La aplicación estará disponible en [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Instalación en Linux/macOS

Los pasos son similares a los de Windows, pero con los siguientes comandos para el entorno virtual:

```bash
# Crear el entorno virtual
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate
```

## Solución de Problemas Comunes

### Error al instalar dependencias

Si encuentras errores al instalar las dependencias, intenta actualizar pip:

```bash
pip install --upgrade pip
```

### Problemas con la base de datos

Si la base de datos no se crea correctamente, puedes intentar eliminar el archivo `instance/mantenimiento.db` y volver a ejecutar `flask init-db`.
