import sqlite3
from database import obtener_conexion

def verificar_login(nombre, password):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre=? AND password=?", (nombre, password))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def obtener_usuario_por_id(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def listar_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, rol, pasillo_asignado FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def crear_usuario(nombre, password, rol, pasillo):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, password, rol, pasillo_asignado) VALUES (?,?,?,?)",
                       (nombre, password, rol, pasillo))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def eliminar_usuario(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()