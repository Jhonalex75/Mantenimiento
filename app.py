from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear base de datos si no existe o actualizarla
def init_db():
    with sqlite3.connect("mantenimiento.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mantenimiento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo TEXT,
                checklist TEXT,
                comentarios TEXT,
                archivo TEXT
            )
        ''')
        try:
            cursor.execute("ALTER TABLE mantenimiento ADD COLUMN archivo TEXT;")
        except sqlite3.OperationalError:
            pass  # La columna ya existe
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    fecha = request.form['fecha']
    tipo = request.form['tipo']
    checklist = ', '.join(request.form.getlist('checklist'))
    comentarios = request.form['comentarios']
    archivo = request.files.get('archivo')
    
    filename = None
    if archivo and archivo.filename:
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(filepath)
    
    with sqlite3.connect("mantenimiento.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mantenimiento (fecha, tipo, checklist, comentarios, archivo) VALUES (?, ?, ?, ?, ?)",
                       (fecha, tipo, checklist, comentarios, filename))
        conn.commit()
    
    return redirect(url_for('historial'))

@app.route('/historial')
def historial():
    with sqlite3.connect("mantenimiento.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mantenimiento ORDER BY fecha DESC")
        registros = cursor.fetchall()
    return render_template('historial.html', registros=registros)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/exportar-excel')
def exportar_excel():
    try:
        with sqlite3.connect("mantenimiento.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, tipo, checklist, comentarios FROM mantenimiento ORDER BY fecha DESC")
            registros = cursor.fetchall()
            
            # Convertir los registros a una lista de diccionarios
            data = [dict(registro) for registro in registros]
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_filename = f'mantenimiento_bomba_warman_{timestamp}.xlsx'
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            
            # Guardar a Excel
            df.to_excel(excel_path, index=False, sheet_name='Mantenimiento')
            
            # Enviar el archivo
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=excel_filename,
                as_attachment=True,
                download_name=excel_filename
            )
            
    except Exception as e:
        print(f"Error al exportar a Excel: {str(e)}")
        return redirect(url_for('historial'))

if __name__ == '__main__':
    app.run(debug=True)
