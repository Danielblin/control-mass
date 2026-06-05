from flask import Flask, render_template, request, redirect, url_for, session, send_file
from database import obtener_conexion, crear_base_datos
from auth import verificar_login, listar_usuarios, crear_usuario, eliminar_usuario
from reports import exportar_reporte_pasillo, exportar_reporte_general, exportar_reporte_completo
from datetime import date, datetime
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_mass_2026'

crear_base_datos()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        usuario = verificar_login(nombre, password)
        if usuario:
            session['user_id'] = usuario[0]
            session['user_nombre'] = usuario[1]
            session['user_rol'] = usuario[3]
            session['user_pasillo'] = usuario[4]
            return redirect(url_for('dashboard'))
        else:
            return "❌ Usuario o contraseña incorrectos"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_rol'] == 'admin':
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('user_pasillo'))

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or session['user_rol'] != 'admin':
        return redirect(url_for('login'))
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, password, rol, pasillo_asignado FROM usuarios")
    usuarios = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lotes WHERE fecha_vencimiento <= date('now', '+7 days')")
    alertas_vencimiento = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(cantidad) FROM mermas WHERE fecha = date('now')")
    mermas_hoy = cursor.fetchone()[0] or 0
    conn.close()
    return render_template('admin.html', usuarios=usuarios, total_productos=total_productos, alertas_vencimiento=alertas_vencimiento, mermas_hoy=mermas_hoy)

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario_route():
    if 'user_id' not in session or session['user_rol'] != 'admin':
        return redirect(url_for('login'))
    nombre = request.form['nombre']
    password = request.form['password']
    rol = request.form['rol']
    pasillo = request.form['pasillo']
    if crear_usuario(nombre, password, rol, pasillo):
        return redirect(url_for('admin_panel'))
    else:
        return "❌ Error: el usuario ya existe"

@app.route('/cambiar_password/<int:user_id>', methods=['POST'])
def cambiar_password(user_id):
    if 'user_id' not in session or session['user_rol'] != 'admin':
        return redirect(url_for('login'))
    
    nueva_password = request.form['nueva_password']
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET password=? WHERE id=?", (nueva_password, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_panel'))

@app.route('/eliminar_usuario/<int:user_id>')
def eliminar_usuario_route(user_id):
    if 'user_id' not in session or session['user_rol'] != 'admin':
        return redirect(url_for('login'))
    eliminar_usuario(user_id)
    return redirect(url_for('admin_panel'))

@app.route('/user_pasillo')
def user_pasillo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pasillo = session['user_pasillo']
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre, precio, uxb FROM productos WHERE pasillo=?", (pasillo,))
    productos_raw = cursor.fetchall()
    productos = []
    for p in productos_raw:
        # Obtener el último conteo (stock contado y diferencia)
        cursor.execute("""
            SELECT stock_contado, diferencia 
            FROM conteos 
            WHERE codigo_producto=? 
            ORDER BY fecha DESC, id DESC 
            LIMIT 1
        """, (p[0],))
        ultimo_conteo = cursor.fetchone()
        if ultimo_conteo:
            stock = ultimo_conteo[0]
            diferencia = ultimo_conteo[1]
        else:
            stock = 0
            diferencia = 0
        productos.append((p[0], p[1], p[2], p[3], stock, diferencia))
    cursor.execute("""
        SELECT p.nombre, l.fecha_vencimiento, l.cantidad, l.codigo_producto 
        FROM lotes l 
        JOIN productos p ON l.codigo_producto = p.codigo 
        WHERE p.pasillo=? AND l.fecha_vencimiento <= date('now', '+7 days') 
        ORDER BY l.fecha_vencimiento
    """, (pasillo,))
    alertas = cursor.fetchall()
    
    # Obtener productos con lotes para la sección de gestión
    productos_con_lotes = []
    for p in productos_raw:
        cursor.execute("SELECT COUNT(*) FROM lotes WHERE codigo_producto=?", (p[0],))
        tiene_lotes = cursor.fetchone()[0] > 0
        productos_con_lotes.append((p[0], p[1], tiene_lotes))
    
    conn.close()
    return render_template('user_pasillo.html', 
                         pasillo=pasillo, 
                         productos=productos,
                         alertas=alertas,
                         productos_con_lotes=productos_con_lotes,
                         usuario=session['user_nombre'])

@app.route('/registrar_conteo', methods=['POST'])
def registrar_conteo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    codigo = request.form['codigo']
    stock_contado = int(request.form['stock_contado'])
    stock_pocket = int(request.form['stock_pocket'])
    diferencia = stock_contado - stock_pocket
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conteos (fecha, codigo_producto, stock_pocket, stock_contado, diferencia, usuario) VALUES (?, ?, ?, ?, ?, ?)", (date.today(), codigo, stock_pocket, stock_contado, diferencia, session['user_nombre']))
    conn.commit()
    conn.close()
    return redirect(url_for('user_pasillo'))

@app.route('/registrar_lote', methods=['POST'])
def registrar_lote():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    codigo = request.form['codigo']
    fecha_vencimiento = request.form['fecha_vencimiento']
    cantidad = int(request.form['cantidad'])
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lotes (codigo_producto, fecha_vencimiento, cantidad, usuario_registra, fecha_registro) VALUES (?, ?, ?, ?, ?)", (codigo, fecha_vencimiento, cantidad, session['user_nombre'], date.today()))
    conn.commit()
    conn.close()
    return redirect(url_for('user_pasillo'))

@app.route('/registrar_merma', methods=['POST'])
def registrar_merma():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    codigo = request.form['codigo']
    cantidad = int(request.form['cantidad'])
    motivo = request.form['motivo']
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mermas (fecha, codigo_producto, cantidad, motivo, usuario) VALUES (?, ?, ?, ?, ?)", (date.today(), codigo, cantidad, motivo, session['user_nombre']))
    conn.commit()
    conn.close()
    return redirect(url_for('user_pasillo'))

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    pasillo = request.form['pasillo']
    uxb = request.form.get('uxb', '')
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Verificar si el producto ya existe
    cursor.execute("SELECT codigo FROM productos WHERE codigo=?", (codigo,))
    existe = cursor.fetchone()
    
    if existe:
        # Si ya existe, actualizar los datos
        cursor.execute("""
            UPDATE productos 
            SET nombre=?, precio=?, pasillo=?, usuario_responsable=?, uxb=? 
            WHERE codigo=?
        """, (nombre, precio, pasillo, session['user_nombre'], uxb, codigo))
        conn.commit()
        conn.close()
        return redirect(url_for('user_pasillo'))
    else:
        # Si no existe, insertar nuevo
        try:
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, precio, pasillo, usuario_responsable, uxb) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (codigo, nombre, precio, pasillo, session['user_nombre'], uxb))
            conn.commit()
            conn.close()
            return redirect(url_for('user_pasillo'))
        except Exception as e:
            conn.rollback()
            conn.close()
            return f"❌ Error al crear el producto: {str(e)}"

@app.route('/exportar_excel')
def exportar_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_rol'] == 'admin':
        archivo = exportar_reporte_general()
    else:
        archivo = exportar_reporte_pasillo(session['user_pasillo'], f'reporte_{session["user_pasillo"]}_{date.today()}.xlsx')
    return send_file(archivo, as_attachment=True)

@app.route('/exportar_completo')
def exportar_completo():
    if 'user_id' not in session or session['user_rol'] != 'admin':
        return redirect(url_for('login'))
    archivo = exportar_reporte_completo()
    return send_file(archivo, as_attachment=True)

@app.route('/ver_conteos')
def ver_conteos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pasillo = session['user_pasillo']
    producto_filtro = request.args.get('producto', '')
    fecha_filtro = request.args.get('fecha', '')
    limite = request.args.get('limite', 20)
    try:
        limite = int(limite)
    except:
        limite = 20
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM productos WHERE pasillo=?", (pasillo,))
    productos_lista = cursor.fetchall()
    query = "SELECT c.fecha, p.nombre, c.stock_pocket, c.stock_contado, c.diferencia, c.usuario FROM conteos c JOIN productos p ON c.codigo_producto = p.codigo WHERE p.pasillo=?"
    params = [pasillo]
    if producto_filtro:
        query += " AND p.codigo=?"
        params.append(producto_filtro)
    if fecha_filtro:
        query += " AND c.fecha=?"
        params.append(fecha_filtro)
    query += " ORDER BY c.fecha DESC LIMIT ?"
    params.append(limite)
    cursor.execute(query, params)
    conteos = cursor.fetchall()
    conn.close()
    return render_template('ver_conteos.html', conteos=conteos, productos=productos_lista, producto_filtro=producto_filtro, fecha_filtro=fecha_filtro, limite=limite)

@app.route('/ver_lotes/<codigo>')
def ver_lotes(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    orden = request.args.get('orden', 'asc')
    hoy = date.today().isoformat()
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM productos WHERE codigo=?", (codigo,))
    producto = cursor.fetchone()
    if orden == 'asc':
        cursor.execute("SELECT fecha_vencimiento, cantidad, usuario_registra, fecha_registro FROM lotes WHERE codigo_producto=? ORDER BY fecha_vencimiento ASC", (codigo,))
    else:
        cursor.execute("SELECT fecha_vencimiento, cantidad, usuario_registra, fecha_registro FROM lotes WHERE codigo_producto=? ORDER BY fecha_vencimiento DESC", (codigo,))
    lotes = cursor.fetchall()
    conn.close()
    return render_template('ver_lotes.html', lotes=lotes, producto=producto, codigo=codigo, orden=orden, hoy=hoy)

@app.route('/eliminar_producto/<codigo>')
def eliminar_producto(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Eliminar primero los lotes asociados
    cursor.execute("DELETE FROM lotes WHERE codigo_producto=?", (codigo,))
    # Eliminar conteos asociados
    cursor.execute("DELETE FROM conteos WHERE codigo_producto=?", (codigo,))
    # Eliminar mermas asociadas
    cursor.execute("DELETE FROM mermas WHERE codigo_producto=?", (codigo,))
    # Finalmente eliminar el producto
    cursor.execute("DELETE FROM productos WHERE codigo=?", (codigo,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('user_pasillo'))

# ========== NUEVAS RUTAS PARA GESTIÓN DE LOTES ==========

@app.route('/gestionar_lotes/<codigo>')
def gestionar_lotes(codigo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    hoy = date.today().isoformat()
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Obtener información del producto
    cursor.execute("SELECT nombre FROM productos WHERE codigo=?", (codigo,))
    producto = cursor.fetchone()
    
    # Obtener todos los lotes del producto
    cursor.execute("""
        SELECT id, fecha_vencimiento, cantidad, usuario_registra, fecha_registro 
        FROM lotes 
        WHERE codigo_producto=? 
        ORDER BY fecha_vencimiento ASC
    """, (codigo,))
    lotes = cursor.fetchall()
    
    conn.close()
    
    return render_template('gestionar_lotes.html', 
                         producto=producto, 
                         codigo=codigo, 
                         lotes=lotes,
                         hoy=hoy)

@app.route('/editar_lote/<int:lote_id>', methods=['POST'])
def editar_lote(lote_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    nueva_cantidad = int(request.form['cantidad'])
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Actualizar la cantidad del lote
    cursor.execute("UPDATE lotes SET cantidad=? WHERE id=?", (nueva_cantidad, lote_id))
    conn.commit()
    
    # Obtener el código del producto para redirigir
    cursor.execute("SELECT codigo_producto FROM lotes WHERE id=?", (lote_id,))
    codigo = cursor.fetchone()[0]
    conn.close()
    
    return redirect(url_for('gestionar_lotes', codigo=codigo))

@app.route('/eliminar_lote/<int:lote_id>')
def eliminar_lote(lote_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Obtener código del producto antes de eliminar
    cursor.execute("SELECT codigo_producto FROM lotes WHERE id=?", (lote_id,))
    codigo = cursor.fetchone()[0]
    
    # Eliminar el lote
    cursor.execute("DELETE FROM lotes WHERE id=?", (lote_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('gestionar_lotes', codigo=codigo))

# ========== FIN NUEVAS RUTAS ==========

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Esto es para PythonAnywhere
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)