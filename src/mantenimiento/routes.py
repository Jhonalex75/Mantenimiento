"""
Módulo de rutas para la aplicación de gestión de mantenimiento.

Este módulo contiene todas las rutas de la aplicación web organizadas en blueprints.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .models.activo import Activo
from .models.falla import Falla, EstadoFalla
from .models.orden_trabajo import OrdenTrabajo
from .utils.kpi_calculator import KPICalculator

# Crear un Blueprint para las rutas
bp = Blueprint('main', __name__)

# Ruta principal
@bp.route('/')
def index():
    """Página principal del sistema."""
    return render_template('index.html')

# Rutas para activos
@bp.route('/activos')
def listar_activos():
    """Lista todos los activos del sistema."""
    try:
        db_manager = current_app.db_manager
        activos = db_manager.get_activos()
        return render_template('activos/lista.html', activos=activos)
    except Exception as e:
        flash(f'Error al cargar los activos: {str(e)}', 'error')
        return render_template('activos/lista.html', activos=[])

# Rutas para fallas
@bp.route('/fallas')
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

# ... (resto de las rutas para fallas)

# Rutas para órdenes de trabajo
@bp.route('/ordenes-trabajo')
def listar_ordenes_trabajo():
    """Lista todas las órdenes de trabajo."""
    try:
        db_manager = current_app.db_manager
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

# APIs
@bp.route('/api/kpis/activo/<int:activo_id>')
def api_kpis_activo(activo_id):
    """API para obtener los KPIs de un activo."""
    try:
        db_manager = current_app.db_manager
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

# Manejo de errores
@bp.app_errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('errores/404.html'), 404

@bp.app_errorhandler(500)
def error_servidor(error):
    return render_template('errores/500.html'), 500
