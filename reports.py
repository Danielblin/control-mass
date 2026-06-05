import pandas as pd
import sqlite3
from datetime import date
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mass_control.db')

def exportar_reporte_pasillo(pasillo, nombre_archivo):
    conn = sqlite3.connect(DB_PATH)
    
    query_productos = f"SELECT codigo, nombre, precio FROM productos WHERE pasillo = '{pasillo}'"
    productos = pd.read_sql_query(query_productos, conn)
    
    query_lotes = f"""
        SELECT p.nombre, l.fecha_vencimiento, l.cantidad
        FROM lotes l
        JOIN productos p ON l.codigo_producto = p.codigo
        WHERE p.pasillo = '{pasillo}'
        ORDER BY l.fecha_vencimiento
    """
    lotes = pd.read_sql_query(query_lotes, conn)
    
    query_conteos = f"""
        SELECT c.fecha, p.nombre, c.stock_pocket, c.stock_contado, c.diferencia
        FROM conteos c
        JOIN productos p ON c.codigo_producto = p.codigo
        WHERE p.pasillo = '{pasillo}'
        ORDER BY c.fecha DESC
        LIMIT 20
    """
    conteos = pd.read_sql_query(query_conteos, conn)
    
    conn.close()
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        productos.to_excel(writer, sheet_name='Productos', index=False)
        lotes.to_excel(writer, sheet_name='Próximos a vencer', index=False)
        conteos.to_excel(writer, sheet_name='Últimos conteos', index=False)
    
    return nombre_archivo

def exportar_reporte_general():
    conn = sqlite3.connect(DB_PATH)
    
    query_resumen = """
        SELECT p.pasillo, 
               COUNT(DISTINCT p.codigo) as total_productos,
               SUM(l.cantidad) as stock_total
        FROM productos p
        LEFT JOIN lotes l ON p.codigo = l.codigo_producto
        GROUP BY p.pasillo
    """
    resumen = pd.read_sql_query(query_resumen, conn)
    
    query_usuarios = "SELECT nombre, rol, pasillo_asignado FROM usuarios"
    usuarios = pd.read_sql_query(query_usuarios, conn)
    
    conn.close()
    
    nombre_archivo = f'reporte_general_{date.today()}.xlsx'
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        resumen.to_excel(writer, sheet_name='Resumen por pasillo', index=False)
        usuarios.to_excel(writer, sheet_name='Usuarios', index=False)
    
    return nombre_archivo

def exportar_reporte_completo():
    conn = sqlite3.connect(DB_PATH)

    productos = pd.read_sql_query(
        "SELECT * FROM productos", conn
    )

    lotes = pd.read_sql_query(
        "SELECT * FROM lotes", conn
    )

    conteos = pd.read_sql_query(
        "SELECT * FROM conteos", conn
    )

    mermas = pd.read_sql_query(
        "SELECT * FROM mermas", conn
    )

    usuarios = pd.read_sql_query(
        "SELECT * FROM usuarios", conn
    )

    conn.close()

    nombre_archivo = f'reporte_completo_{date.today()}.xlsx'

    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        productos.to_excel(writer, sheet_name='Productos', index=False)
        lotes.to_excel(writer, sheet_name='Lotes', index=False)
        conteos.to_excel(writer, sheet_name='Conteos', index=False)
        mermas.to_excel(writer, sheet_name='Mermas', index=False)
        usuarios.to_excel(writer, sheet_name='Usuarios', index=False)

    return nombre_archivo