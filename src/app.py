"""
Aplicación principal del sistema de gestión de mantenimiento.

Este módulo proporciona la interfaz web para el sistema de gestión de mantenimiento,
integrando los módulos de modelos, base de datos y utilidades.
"""

import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime

# Importar módulos propios
from utils.database import DatabaseManager
from utils.data_loader import DataLoader
from utils.kpi_calculator import KPICalculator
from models import Activo, Falla, OrdenTrabajo

# Configuración de la aplicación
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')

# Configuración de rutas
UPLOAD_FOLDER = 'uploads'
BACKUP_FOLDER = 'backups'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que existan los directorios necesarios
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(BACKUP_FOLDER).mkdir(exist_ok=True)

# Inicializar el gestor de base de datos
db_manager = DatabaseManager("mantenimiento.db")

# Cargar datos de ejemplo si la base de datos está vacía
def cargar_datos_iniciales():
    """Carga datos de ejemplo si la base de datos está vacía."""
    try:
        # Verificar si ya hay datos
        activos = db_manager.execute_query("SELECT COUNT(*) as count FROM activos")
        if activos and activos[0]['count'] == 0:
            # Cargar datos de ejemplo
            datos = DataLoader.cargar_datos_ejemplo("data/example")
            
            # Insertar datos en la base de datos
            for tipo, objetos in datos.items():
                DataLoader.insertar_en_bd(objetos, db_manager)
            
            print("Datos de ejemplo cargados correctamente.")
    except Exception as e:
        print(f"Error al cargar datos iniciales: {e}")

# Llamar a la función para cargar datos iniciales
cargar_datos_iniciales()

# Rutas de la aplicación
@app.route('/')
def index():
    """Página principal del sistema."""
    return render_template('index.html')

@app.route('/activos')
def listar_activos():
    """Lista todos los activos del sistema."""
    try:
        activos = db_manager.get_activos()
        return render_template('activos/lista.html', activos=activos)
    except Exception as e:
        flash(f'Error al cargar los activos: {str(e)}', 'error')
        return render_template('activos/lista.html', activos=[])

@app.route('/activos/nuevo', methods=['GET', 'POST'])
def nuevo_activo():
    """Maneja la creación de un nuevo activo."""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            datos = {
                'nombre': request.form.get('nombre'),
                'criticidad': request.form.get('criticidad'),
                'fecha_alta': request.form.get('fecha_alta') or datetime.now().strftime('%Y-%m-%d'),
                'ubicacion': request.form.get('ubicacion', ''),
                'responsable': request.form.get('responsable', ''),
                'estado': request.form.get('estado', 'Activo'),
                'horas_operacion': float(request.form.get('horas_operacion', 0)),
                'proximo_mantenimiento': request.form.get('proximo_mantenimiento')
            }
            
            # Validar datos requeridos
            if not datos['nombre'] or not datos['criticidad']:
                flash('Nombre y criticidad son campos requeridos', 'error')
                return render_template('activos/formulario.html', activo=datos)
            
            # Insertar en la base de datos
            activo_id = db_manager.insert_activo(datos)
            flash(f'Activo creado correctamente con ID: {activo_id}', 'success')
            return redirect(url_for('ver_activo', activo_id=activo_id))
            
        except Exception as e:
            flash(f'Error al crear el activo: {str(e)}', 'error')
            return render_template('activos/formulario.html', activo=request.form)
    
    # Mostrar formulario vacío para GET
    return render_template('activos/formulario.html', activo={})

@app.route('/activos/<int:activo_id>')
def ver_activo(activo_id):
    """Muestra los detalles de un activo específico."""
    try:
        activo = db_manager.get_activo(activo_id)
        if not activo:
            flash('Activo no encontrado', 'error')
            return redirect(url_for('listar_activos'))
        
        # Obtener fallas del activo
        fallas = db_manager.execute_query(
            "SELECT * FROM fallas WHERE activo_id = ? ORDER BY fecha_reporte DESC",
            (activo_id,)
        )
        
        # Obtener órdenes de trabajo del activo
        ordenes = db_manager.execute_query(
            """
            SELECT * FROM ordenes_trabajo 
            WHERE activo_id = ? 
            ORDER BY fecha_creacion DESC
            """,
            (activo_id,)
        )
        
        # Calcular KPIs
        kpis = KPICalculator.calcular_kpis_activo(fallas, ordenes)
        
        return render_template(
            'activos/detalle.html',
            activo=activo,
            fallas=fallas,
            ordenes=ordenes,
            kpis=kpis
        )
        
    except Exception as e:
        flash(f'Error al cargar el activo: {str(e)}', 'error')
        return redirect(url_for('listar_activos'))

@app.route('/fallas')
def listar_fallas():
    """Lista todas las fallas reportadas con opciones de filtrado."""
    try:
        # Obtener parámetros de filtrado
        estado = request.args.get('estado', '')
        prioridad = request.args.get('prioridad', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        activo_id = request.args.get('activo_id', '')
        
        # Construir la consulta base
        query = """
            SELECT f.*, a.nombre as nombre_activo 
            FROM fallas f
            LEFT JOIN activos a ON f.activo_id = a.activo_id
            WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if estado:
            query += " AND f.estado = ?"
            params.append(estado)
            
        if prioridad:
            query += " AND f.prioridad = ?"
            params.append(int(prioridad))
            
        if fecha_desde:
            query += " AND DATE(f.fecha_reporte) >= ?"
            params.append(fecha_desde)
            
        if fecha_hasta:
            query += " AND DATE(f.fecha_reporte) <= ?"
            params.append(fecha_hasta)
            
        if activo_id:
            query += " AND f.activo_id = ?"
            params.append(int(activo_id))
        
        # Ordenar por fecha de reporte descendente
        query += " ORDER BY f.fecha_reporte DESC"
        
        # Obtener las fallas filtradas
        fallas = db_manager.execute_query(query, tuple(params))
        
        # Obtener lista de activos para el filtro
        activos = db_manager.execute_query("SELECT activo_id, nombre FROM activos ORDER BY nombre")
        
        return render_template('fallas/lista.html', 
                             fallas=fallas, 
                             activos=activos,
                             filtros={
                                 'estado': estado,
                                 'prioridad': prioridad,
                                 'fecha_desde': fecha_desde,
                                 'fecha_hasta': fecha_hasta,
                                 'activo_id': activo_id
                             })
    except Exception as e:
        flash(f'Error al cargar las fallas: {str(e)}', 'error')
        return render_template('fallas/lista.html', fallas=[], activos=[])

@app.route('/fallas/nueva', methods=['GET', 'POST'])
def reportar_falla():
    """Maneja el reporte de una nueva falla."""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            datos = {
                'activo_id': request.form.get('activo_id'),
                'descripcion': request.form.get('descripcion'),
                'prioridad': int(request.form.get('prioridad', 3)),
                'reportada_por': request.form.get('reportada_por', 'Sistema'),
                'causa_raiz': request.form.get('causa_raiz', ''),
                'acciones_tomadas': request.form.get('acciones_tomadas', ''),
                'asignado_a': request.form.get('asignado_a')
            }
            
            # Validar datos requeridos
            if not datos['activo_id'] or not datos['descripcion']:
                flash('El activo y la descripción son campos requeridos', 'error')
                return redirect(url_for('reportar_falla'))
            
            # Insertar la falla en la base de datos
            falla_id = db_manager.insert_falla(datos)
            
            # Manejar archivos adjuntos si los hay
            if 'documentos' in request.files:
                for file in request.files.getlist('documentos'):
                    if file.filename != '':
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'falla_{falla_id}_{filename}')
                        file.save(filepath)
                        # Guardar referencia en la base de datos
                        db_manager.insert_documento({
                            'tipo_entidad': 'falla',
                            'entidad_id': falla_id,
                            'nombre_archivo': filename,
                            'ruta_archivo': filepath,
                            'tipo_mime': file.mimetype,
                            'tamano': os.path.getsize(filepath)
                        })
            
            flash('Falla reportada correctamente', 'success')
            return redirect(url_for('ver_falla', falla_id=falla_id))
            
        except Exception as e:
            flash(f'Error al reportar la falla: {str(e)}', 'error')
            return redirect(url_for('reportar_falla'))
    
    # Para GET, mostrar el formulario de reporte
    activos = db_manager.execute_query("SELECT activo_id, nombre FROM activos WHERE estado = 'Activo' ORDER BY nombre")
    tecnicos = db_manager.execute_query("SELECT DISTINCT tecnico_asignado FROM ordenes_trabajo WHERE tecnico_asignado IS NOT NULL")
    return render_template('fallas/formulario.html', 
                         falla=None, 
                         activos=activos, 
                         tecnicos=[t['tecnico_asignado'] for t in tecnicos if t['tecnico_asignado']])

@app.route('/fallas/<int:falla_id>')
def ver_falla(falla_id):
    """Muestra los detalles de una falla específica."""
    try:
        # Obtener la falla con información del activo
        falla = db_manager.execute_query(
            """
            SELECT f.*, a.nombre as nombre_activo, a.criticidad, a.ubicacion
            FROM fallas f
            LEFT JOIN activos a ON f.activo_id = a.activo_id
            WHERE f.falla_id = ?
            """,
            (falla_id,)
        )
        
        if not falla:
            flash('Falla no encontrada', 'error')
            return redirect(url_for('listar_fallas'))
        
        falla = falla[0]  # Obtener el primer (y único) resultado
        
        # Obtener documentos adjuntos
        documentos = db_manager.execute_query(
            "SELECT * FROM documentos WHERE tipo_entidad = 'falla' AND entidad_id = ?",
            (falla_id,)
        )
        
        # Obtener órdenes de trabajo relacionadas
        ordenes = db_manager.execute_query(
            """
            SELECT ot.*, a.nombre as nombre_activo
            FROM ordenes_trabajo ot
            LEFT JOIN activos a ON ot.activo_id = a.activo_id
            WHERE ot.activo_id = ?
            ORDER BY ot.fecha_creacion DESC
            """,
            (falla['activo_id'],)
        )
        
        # Obtener historial de cambios
        historial = db_manager.execute_query(
            """
            SELECT * FROM historial_cambios
            WHERE entidad = 'falla' AND entidad_id = ?
            ORDER BY fecha_cambio DESC
            """,
            (falla_id,)
        )
        
        return render_template('fallas/detalle.html',
                             falla=falla,
                             documentos=documentos,
                             ordenes=ordenes,
                             historial=historial)
        
    except Exception as e:
        flash(f'Error al cargar la falla: {str(e)}', 'error')
        return redirect(url_for('listar_fallas'))

@app.route('/fallas/<int:falla_id>/editar', methods=['GET', 'POST'])
def editar_falla(falla_id):
    """Edita una falla existente."""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            datos = {
                'falla_id': falla_id,
                'activo_id': request.form.get('activo_id'),
                'descripcion': request.form.get('descripcion'),
                'prioridad': int(request.form.get('prioridad', 3)),
                'estado': request.form.get('estado'),
                'causa_raiz': request.form.get('causa_raiz', ''),
                'acciones_tomadas': request.form.get('acciones_tomadas', ''),
                'asignado_a': request.form.get('asignado_a', None),
                'tiempo_fuera_servicio_h': float(request.form.get('tiempo_fuera_servicio_h', 0)),
                'costo_reparacion': float(request.form.get('costo_reparacion', 0)) or None
            }
            
            # Validar datos requeridos
            if not datos['activo_id'] or not datos['descripcion'] or not datos['estado']:
                flash('Los campos activo, descripción y estado son requeridos', 'error')
                return redirect(url_for('editar_falla', falla_id=falla_id))
            
            # Actualizar la falla en la base de datos
            db_manager.update_falla(datos)
            
            # Registrar el cambio en el historial
            db_manager.registrar_cambio(
                entidad='falla',
                entidad_id=falla_id,
                usuario=request.form.get('usuario', 'Sistema'),
                campo='actualizacion',
                valor_anterior='',
                valor_nuevo='Falla actualizada',
                notas=f'Actualización de la falla {falla_id}'
            )
            
            flash('Falla actualizada correctamente', 'success')
            return redirect(url_for('ver_falla', falla_id=falla_id))
            
        except Exception as e:
            flash(f'Error al actualizar la falla: {str(e)}', 'error')
            return redirect(url_for('editar_falla', falla_id=falla_id))
    
    # Para GET, mostrar el formulario de edición
    try:
        falla = db_manager.get_falla(falla_id)
        if not falla:
            flash('Falla no encontrada', 'error')
            return redirect(url_for('listar_fallas'))
            
        activos = db_manager.execute_query("SELECT activo_id, nombre FROM activos ORDER BY nombre")
        tecnicos = db_manager.execute_query("SELECT DISTINCT tecnico_asignado FROM ordenes_trabajo WHERE tecnico_asignado IS NOT NULL")
        
        return render_template('fallas/formulario.html', 
                             falla=falla, 
                             activos=activos, 
                             tecnicos=[t['tecnico_asignado'] for t in tecnicos if t['tecnico_asignado']],
                             modo_edicion=True)
        
    except Exception as e:
        flash(f'Error al cargar la falla para edición: {str(e)}', 'error')
        return redirect(url_for('listar_fallas'))

@app.route('/fallas/<int:falla_id>/eliminar', methods=['POST'])
def eliminar_falla(falla_id):
    """Elimina una falla del sistema."""
    if request.method == 'POST':
        try:
            # Verificar si la falla existe
            falla = db_manager.get_falla(falla_id)
            if not falla:
                flash('Falla no encontrada', 'error')
                return redirect(url_for('listar_fallas'))
            
            # Verificar si hay órdenes de trabajo relacionadas
            ordenes = db_manager.execute_query(
                "SELECT COUNT(*) as total FROM ordenes_trabajo WHERE falla_id = ?",
                (falla_id,)
            )
            
            if ordenes and ordenes[0]['total'] > 0:
                flash('No se puede eliminar la falla porque tiene órdenes de trabajo asociadas', 'error')
                return redirect(url_for('ver_falla', falla_id=falla_id))
            
            # Eliminar documentos adjuntos
            documentos = db_manager.execute_query(
                "SELECT * FROM documentos WHERE tipo_entidad = 'falla' AND entidad_id = ?",
                (falla_id,)
            )
            
            for doc in documentos:
                try:
                    if os.path.exists(doc['ruta_archivo']):
                        os.remove(doc['ruta_archivo'])
                except Exception as e:
                    print(f"Error al eliminar archivo {doc['ruta_archivo']}: {str(e)}")
            
            # Eliminar registros de documentos en la base de datos
            db_manager.execute_query(
                "DELETE FROM documentos WHERE tipo_entidad = 'falla' AND entidad_id = ?",
                (falla_id,)
            )
            
            # Eliminar la falla
            db_manager.execute_query("DELETE FROM fallas WHERE falla_id = ?", (falla_id,))
            
            # Registrar la eliminación en el historial
            db_manager.registrar_cambio(
                entidad='falla',
                entidad_id=falla_id,
                usuario=request.form.get('usuario', 'Sistema'),
                campo='eliminacion',
                valor_anterior=f"Falla {falla_id}",
                valor_nuevo='',
                notas=f"Falla eliminada. Motivo: {request.form.get('motivo', 'No especificado')}"
            )
            
            flash('Falla eliminada correctamente', 'success')
            return redirect(url_for('listar_fallas'))
            
        except Exception as e:
            flash(f'Error al eliminar la falla: {str(e)}', 'error')
            return redirect(url_for('ver_falla', falla_id=falla_id))
    
    return redirect(url_for('listar_fallas'))

@app.route('/api/fallas/estados')
def api_estados_fallas():
    """API para obtener los estados disponibles de las fallas."""
    try:
        estados = [e.value for e in EstadoFalla]
        return jsonify(estados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fallas/prioridades')
def api_prioridades_fallas():
    """API para obtener las prioridades disponibles de las fallas."""
    try:
        prioridades = [
            {"id": 1, "nombre": "Crítica"},
            {"id": 2, "nombre": "Alta"},
            {"id": 3, "nombre": "Media"},
            {"id": 4, "nombre": "Baja"},
            {"id": 5, "nombre": "Informativa"}
        ]
        return jsonify(prioridades)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ordenes-trabajo')
def listar_ordenes_trabajo():
    """Lista todas las órdenes de trabajo."""
    try:
        ordenes = db_manager.execute_query(
            """
            SELECT o.*, a.nombre as nombre_activo 
            FROM ordenes_trabajo o
            LEFT JOIN activos a ON o.activo_id = a.activo_id
            ORDER BY o.fecha_creacion DESC
            """
        )
        return render_template('ordenes/lista.html', ordenes=ordenes)
    except Exception as e:
        flash(f'Error al cargar las órdenes de trabajo: {str(e)}', 'error')
        return render_template('ordenes/lista.html', ordenes=[])

@app.route('/api/kpis/activo/<int:activo_id>')
def api_kpis_activo(activo_id):
    """API para obtener los KPIs de un activo."""
    try:
        fallas = db_manager.execute_query(
            "SELECT * FROM fallas WHERE activo_id = ?",
            (activo_id,)
        )
        
        ordenes = db_manager.execute_query(
            "SELECT * FROM ordenes_trabajo WHERE activo_id = ?",
            (activo_id,)
        )
        
        kpis = KPICalculator.calcular_kpis_activo(fallas, ordenes)
        return jsonify(kpis)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/estadisticas')
def api_estadisticas():
    """API para obtener estadísticas generales."""
    try:
        # Obtener totales
        total_activos = db_manager.execute_query("SELECT COUNT(*) as count FROM activos")[0]['count']
        total_fallas = db_manager.execute_query("SELECT COUNT(*) as count FROM fallas")[0]['count']
        total_ordenes = db_manager.execute_query("SELECT COUNT(*) as count FROM ordenes_trabajo")[0]['count']
        
        # Obtener fallas por activo
        fallas_por_activo = db_manager.execute_query(
            """
            SELECT a.nombre, COUNT(f.falla_id) as total
            FROM activos a
            LEFT JOIN fallas f ON a.activo_id = f.activo_id
            GROUP BY a.activo_id, a.nombre
            ORDER BY total DESC
            """
        )
        
        # Obtener tiempo promedio de reparación por activo
        tiempo_promedio_reparacion = db_manager.execute_query(
            """
            SELECT a.nombre, AVG(f.tiempo_fuera_servicio_h) as promedio_horas
            FROM fallas f
            JOIN activos a ON f.activo_id = a.activo_id
            WHERE f.estado = 'Resuelta' OR f.estado = 'Cerrada'
            GROUP BY a.activo_id, a.nombre
            """
        )
        
        return jsonify({
            'totales': {
                'activos': total_activos,
                'fallas': total_fallas,
                'ordenes_trabajo': total_ordenes
            },
            'fallas_por_activo': fallas_por_activo,
            'tiempo_promedio_reparacion': tiempo_promedio_reparacion
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errores/404.html'), 404

@app.errorhandler(500)
def error_servidor(error):
    return render_template('errores/500.html'), 500

if __name__ == '__main__':
    # Crear tablas si no existen
    db_manager._create_tables()
    
    # Iniciar la aplicación
    app.run(debug=True)
