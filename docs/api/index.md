# Documentación de la API

Bienvenido a la documentación de la API del Sistema de Gestión de Mantenimiento. Esta API RESTful permite la integración con otros sistemas y el acceso programático a los datos de mantenimiento.

## Autenticación

Todas las solicitudes a la API requieren autenticación mediante token JWT. Incluye el token en el encabezado de autorización:

```
Authorization: Bearer <tu_token_jwt>
```

## Estructura de Respuesta

Todas las respuestas exitosas siguen el siguiente formato:

```json
{
  "status": "success",
  "data": {},
  "message": "Operación exitosa"
}
```

## Códigos de Estado HTTP

- `200 OK` - La solicitud se completó exitosamente
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Error en la solicitud (validación fallida, datos faltantes, etc.)
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - No autorizado para realizar la acción
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

## Endpoints Disponibles

### Autenticación
- `POST /api/auth/login` - Iniciar sesión y obtener token
- `POST /api/auth/refresh` - Refrescar token de acceso
- `POST /api/auth/logout` - Cerrar sesión

### Activos
- `GET /api/activos` - Listar todos los activos
- `POST /api/activos` - Crear un nuevo activo
- `GET /api/activos/<id>` - Obtener detalles de un activo
- `PUT /api/activos/<id>` - Actualizar un activo
- `DELETE /api/activos/<id>` - Eliminar un activo

### Fallas
- `GET /api/fallas` - Listar todas las fallas
- `POST /api/fallas` - Reportar una nueva falla
- `GET /api/fallas/<id>` - Obtener detalles de una falla
- `PUT /api/fallas/<id>` - Actualizar una falla
- `DELETE /api/fallas/<id>` - Eliminar una falla

### Órdenes de Trabajo
- `GET /api/ordenes` - Listar todas las órdenes de trabajo
- `POST /api/ordenes` - Crear una nueva orden de trabajo
- `GET /api/ordenes/<id>` - Obtener detalles de una orden
- `PUT /api/ordenes/<id>` - Actualizar una orden
- `DELETE /api/ordenes/<id>` - Eliminar una orden

## Ejemplo de Uso

### Autenticación

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Listar Activos

```bash
curl -X GET http://localhost:5000/api/activos \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Crear una Nueva Falla

```bash
curl -X POST http://localhost:5000/api/fallas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -d '{
    "activo_id": 1,
    "descripcion": "Falla en el motor principal",
    "fecha_reporte": "2025-08-13T10:00:00Z",
    "prioridad": "alta"
  }'
```
