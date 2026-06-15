import sqlite3
from datetime import date
import os

# PythonAnywhere usa rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mass_control.db')

def crear_base_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            password TEXT,
            rol TEXT,
            pasillo_asignado TEXT
        )
    ''')
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            precio REAL,
            pasillo TEXT,
            usuario_responsable TEXT,
            uxb TEXT
        )
    ''')
    
    # Tabla de lotes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_producto TEXT,
            fecha_vencimiento DATE,
            cantidad INTEGER,
            usuario_registra TEXT,
            fecha_registro DATE
        )
    ''')
    
    # Tabla de conteos (CON COLUMNA HORA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conteos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            codigo_producto TEXT,
            stock_pocket INTEGER,
            stock_contado INTEGER,
            diferencia INTEGER,
            usuario TEXT,
            hora TEXT
        )
    ''')
    
    # Tabla de mermas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mermas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            codigo_producto TEXT,
            cantidad INTEGER,
            motivo TEXT,
            usuario TEXT
        )
    ''')
    
    # ========== NUEVA TABLA: NOTAS (AGENDA/APUNTES) ==========
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            titulo TEXT,
            descripcion TEXT,
            prioridad TEXT,
            estado TEXT,
            fecha_creacion DATE
        )
    ''')
    # ========== FIN TABLA NOTAS ==========
    
    # Usuario admin por defecto
    cursor.execute("SELECT * FROM usuarios WHERE nombre='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (nombre, password, rol, pasillo_asignado) VALUES (?, ?, ?, ?)",
                       ('admin', 'admin123', 'admin', 'todos'))
    
    # Usuario de ejemplo
    cursor.execute("SELECT * FROM usuarios WHERE nombre='Ana'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (nombre, password, rol, pasillo_asignado) VALUES (?, ?, ?, ?)",
                       ('Ana', 'ana123', 'user', 'Lácteos'))
    
    # Si la tabla conteos ya existía sin la columna hora, agrégala
    try:
        cursor.execute("ALTER TABLE conteos ADD COLUMN hora TEXT")
    except:
        pass  # La columna ya existe
    
    # Si la tabla notas ya existía sin alguna columna, agrégala (por si acaso)
    try:
        cursor.execute("ALTER TABLE notas ADD COLUMN descripcion TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE notas ADD COLUMN prioridad TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE notas ADD COLUMN estado TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE notas ADD COLUMN fecha_creacion DATE")
    except:
        pass
    
    conn.commit()
    conn.close()
    print("✅ Base de datos creada correctamente")

def obtener_conexion():
    return sqlite3.connect(DB_PATH)

if __name__ == '__main__':
    crear_base_datos()