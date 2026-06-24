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
    
    # Tabla de productos (CON COLUMNA IMAGEN)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            precio REAL,
            pasillo TEXT,
            usuario_responsable TEXT,
            uxb TEXT,
            imagen TEXT
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
    
    # ========== NUEVO USUARIO: CARLOS CON PRODUCTOS PRECARGADOS ==========
    cursor.execute("SELECT * FROM usuarios WHERE nombre='Carlos'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (nombre, password, rol, pasillo_asignado) VALUES (?, ?, ?, ?)",
                       ('Carlos', 'carlos123', 'user', 'Lácteos y Abarrotes'))
    
    # Lista de productos para Carlos (con imagen vacía por defecto)
    productos_carlos = [
        ('7751271034319', 'PURA VIDA MEZCLA LACTEA LT390G 6PK', 12.00, 'CJ 8 UN'),
        ('7751271034180', 'GLORIA LECHE ZERO LACTO LT390G', 4.00, 'CJ 24 UN'),
        ('7751271034302', 'PURA VIDA MEZCLA LACTEA LT390GR', 2.90, 'CJ 24 UN'),
        ('7751271034081', 'GLORIA LECHE RECONST ENTERA LT390GR', 3.90, 'CJ 24 UN'),
        ('8445290401182', 'IDEAL CREMOSITA MEZCLA LACTEA LT390GR', 3.70, 'UN 24 UN'),
        ('7751271034135', 'GLORIA LECHE LIGHT LT390GR', 4.00, 'CJ 24 UN'),
        ('8445290404787', 'IDEAL CREMOSITA MEZCLA LACT LT390GR 6PK', 18.00, 'UN 1 UN'),
        ('7751271034098', 'GLORIA LECHE RECONST ENTERA LT390GR 6PK', 21.90, 'CJ 8 UN'),
        ('2200205014743', 'VILLAFRESCA LECHE EVAP LIGHT LT 410GR', 3.50, 'CJ 12 UN'),
        ('2200205014675', 'VILLAFRESCA LECHE EVAP ENTERA LT 410GR', 3.50, 'CJ 12 UN'),
        ('7750632006026', 'VIGOR LECHE UHT PARC DESCREMAD BL 800ML', 3.90, 'UN 12 UN'),
        ('7750151001779', 'LA PREFERIDA MEZCLA LACTEA BL800ML', 3.00, 'CJ 16 UN'),
        ('2200205011841', 'VILLAFRESCA LECHE UHT ENTERA BL 800 ML', 3.90, 'CJ 12 UN'),
        ('7751271036245', 'GLORIA LECHE UHT ENTERA BL800ML', 4.70, 'UN 12 UN'),
        ('7750151008174', 'LAIVE LECHE BOLSITARRO BL390GR', 2.90, 'CJ 24 UN'),
        ('7750151009546', 'LAIVE VIO BB DE ALMENDRA BL 800ML', 6.90, 'CJ 14 UN'),
        ('7751271036252', 'GLORIA-LECHE-UHT-LIGHT-BL800ML', 4.90, 'UN 12 UN'),
        ('7750151506694', 'LA PREFERIDA BEBIDA SABOR CHOCO BL800ML', 3.50, 'CJ 16 UN'),
        ('7751271021913', 'GLORIA LECHE EN POLVO ENTERA BL96GR', 4.50, 'CJ 48 UN'),
        ('7756378000441', 'ONZA STEVIA POTE 60GR', 9.90, 'CJ 12 UN'),
        ('7707242400065', 'PRONALCE DEL SUR AVENA EN HOJUELA 250G', 1.90, 'CJ 24 UN'),
        ('7709476004712', 'COSEC IMPER CEREA AVENA VAINILLA 250GR', 2.90, 'CJ 28 UN'),
        ('7755477575041', 'GRANO DE ORO AVENA QUINUA BL 370GR', 4.90, 'PQ 20 UN'),
        ('2200205694211', 'AVENLY AVENA TRADICIONAL BL 100 GR', 0.80, 'BOL 24 UN'),
        ('7758574007149', 'QUAKER AVENA TRADICIONAL ORIGINAL BL 70G', 1.00, 'CJ 48 UN'),
        ('7758574007088', 'QUAKER AVENA TRADICIONAL ORIGINAL BL750G', 7.90, 'CJ 10 UN'),
        ('2200203190715', 'EL GRANELITO AZUCAR RUBIA 650G', 2.00, 'BOL 36 UN'),
        ('2200203190685', 'EL GRANELITO AZUCAR RUBIA BL 1.3KG', 4.00, 'BOL 18 UN'),
        ('2200203190678', 'EL GRANELITO AZUCAR RUBIA BL 4KG', 12.20, 'BOL 6 UN'),
        ('7758950000894', 'ARROZ EXTRA FARAON AZUL BL X5KG', 22.50, 'BOL 4 UN'),
        ('7757018000494', 'SOMOS DEL NORTE ARROZ EXTRA BL 4KG', 15.60, 'PQ 5 UN'),
        ('7757018000517', 'SOMOS DEL NORTE ARROZ SUPERIOR BL 4KG', 14.70, 'PQ 5 UN'),
        ('7757018000739', 'SOMOS DEL NORTE ARROZ SUPERIOR BL2KG', 7.90, 'BOL 7 UN'),
        ('7754294000095', 'FARAON ARROZ EXTRA AÑEJO NARANJA BL5KG', 25.90, 'BOL 4 UN'),
        ('7757018000548', 'SOMOS DEL NORTE ARROZ FAMILIAR BL 4KG', 13.90, 'PQ 5 UN'),
        ('7754294000071', 'FARAON ARROZ EXTRA AÑEJO NARANJA BL750GR', 4.40, 'BOL 20 UN'),
        ('7758950000962', 'ARROZ EXTRA FARAON AZUL BL750G', 3.90, 'BOL 20 UN'),
        ('7757018000555', 'SOMOS DEL NORTE ARROZ INTEGRAL 650GR', 2.90, 'PQ 30 UN'),
        ('7757018000487', 'SOMOS DEL NORTE ARROZ EXTRA BL 650GR', 2.70, 'PQ 30 UN'),
        ('7757018000531', 'SOMOS DEL NORTE ARROZ FAMILIAR BL 650GR', 2.50, 'PQ 30 UN'),
        ('7757018000500', 'SOMOS DEL NORTE ARROZ SUPERIOR 650GR', 2.60, 'PQ 30 UN'),
        ('2200202785257', 'EL GRANELITO POP CORN BL 400GR', 2.90, 'BOL 10 UN'),
        ('2200202785219', 'EL GRANELITO LENTEJA BL 400GR', 3.90, 'BOL 10 UN'),
        ('2200202785288', 'EL GRANELITO LENTEJA BEBE BL 400GR', 3.00, 'BOL 10 UN'),
        ('2200205062836', 'EL GRANELITO PAPA SECA BL 400GR', 3.90, 'BOL 10 UN'),
        ('2200205062867', 'EL GRANELITO TRIGO MOTE BL 400GR', 2.70, 'BOL 10 UN'),
        ('2200202785271', 'EL GRANELITO GARBANZO BL 400GR', 3.50, 'BOL 10 UN'),
        ('2200205062843', 'EL GRANELITO PALLAR BL 400GR', 4.50, 'BOL 10 UN'),
        ('2200202785301', 'EL GRANELITO FRIJOL PANAMITO BL 400GR', 3.70, 'BOL 10 UN'),
        ('2200205062874', 'EL GRANELITO FRIJOL CASTILLA BL 400GR', 3.90, 'BOL 10 UN'),
        ('2200205062850', 'EL GRANELITO FRIJOL CANARIO BL 400GR', 5.50, 'BOL 10 UN'),
        ('2200205062829', 'EL GRANELITO QUINUA BL 400GR', 5.50, 'BOL 10 UN'),
        ('2200202785202', 'EL GRANELITO ARVERJA PARTIDA BL 400GR', 2.90, 'BOL 10 UN'),
        ('7750262003648', 'OLIBEL ACEITE DE AJONJOLI BT 100ML', 2.50, 'CJ 24 UN'),
        ('2200205036974', 'DELIOLIO ACEITE OLIVA EXT VIRG BT200ML', 10.90, 'CJ 12 UN'),
        ('7750262003662', 'OLIBEL ACEITE DE OLIVA PURO BT 200ML', 9.90, 'CJ 12 UN'),
        ('2200205685424', 'TALLARIN BANCHETTO BL 500G', 2.20, 'PK 20 UN'),
        ('2200205685400', 'SPAGUETTI BANCHETTO BL 500G', 2.20, 'PK 20 UN'),
        ('2200205685394', 'TALLARIN BANCHETTO BL 900G', 3.90, 'PK 12 UN'),
        ('2200205685417', 'SPAGUETTI BANCHETTO BL900G', 3.90, 'PK 12 UN'),
        ('7750243072588', 'DON VITTORIO FIDEO SPAGHETTI BL 950G', 5.50, 'CJ 12 UN'),
        ('7750243082501', 'DON VITTORIO FID SPAGHETTI BL 500G', 3.40, 'CJ 20 UN'),
        ('7750243082532', 'DON VITTORIO FID LINGUINI BL 500G', 3.40, 'CJ 20 UN'),
        ('7750243037549', 'DON VITT FID CAB.ANGEL BL 250 GR', 1.80, 'PQ 40 UN'),
        ('2200205682980', 'BANCHETTO CABELLO DE ANGEL X 250G', 1.20, 'CJ 20 UN'),
        ('7750243074209', 'ALIANZA TORNILLO BL225G', 1.10, 'CJ 20 UN'),
        ('7750243074223', 'ALIANZA CANUTO CHICO 235G', 1.20, 'CJ 20 UN'),
        ('7750243074216', 'ALIANZA CODO RAYADO 225G', 1.10, 'CJ 20 UN'),
        ('7750243082358', 'DON VITTORIO FID RIGATONI BL 250G', 1.80, 'CJ 20 UN'),
        ('7750243082341', 'DON VITTORIO FID CODO RAYADO BL 250G', 1.80, 'CJ 20 UN'),
        ('7750243082334', 'DON VITTORIO FID CANUTO RAYADO BL 250G', 1.80, 'CJ 20 UN'),
        ('7750243082365', 'DON VITTORIO FID TORNILLO BL 250G', 1.80, 'CJ 20 UN'),
        ('7750885023016', 'MOLITALIA FID. PENSALDA TORNILLO BL235G', 3.50, 'BOL 20 UN'),
        ('7750885012515', 'MOLITALIA FID. PENSALDA TORNILLO BL250G', 1.90, 'PQ 20 UN'),
        ('7798316700990', 'SIGLO DE ORO ACEITE VEGETAL BT 3LT', 18.20, 'CJ 6 UN')
    ]
    
    for producto in productos_carlos:
        cursor.execute("SELECT codigo FROM productos WHERE codigo=?", (producto[0],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, precio, pasillo, usuario_responsable, uxb, imagen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (producto[0], producto[1], producto[2], 'Lácteos y Abarrotes', 'Carlos', producto[3], ''))
    
    # ========== FIN PRODUCTOS CARLOS ==========
    
    # Si la tabla conteos ya existía sin la columna hora, agrégala
    try:
        cursor.execute("ALTER TABLE conteos ADD COLUMN hora TEXT")
    except:
        pass  # La columna ya existe
    
    # Si la tabla productos no tiene columna imagen, agrégala
    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN imagen TEXT")
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