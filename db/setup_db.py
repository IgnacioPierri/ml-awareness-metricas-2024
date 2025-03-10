import sqlite3
import os

# Ruta donde se almacenará la base de datos
DB_PATH = "../db/database.db"

# 🔥 Si ya existe una base de datos en la ruta especificada, la eliminamos
# Esto se hace para evitar inconsistencias y asegurarnos de empezar con un entorno limpio.
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# 🔥 Crear la base de datos y establecer la conexión
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Habilitar las claves foráneas en SQLite.
# Por defecto, SQLite no las habilita, por lo que es necesario ejecutar esta instrucción
# para que las restricciones de claves foráneas funcionen correctamente.
cursor.execute("PRAGMA foreign_keys = ON;")

# 🔹 Crear la tabla "usuarios" si no existe
# Esta tabla almacena la información de cada colaborador y tiene las siguientes restricciones:
# - USERNAME: único y no nulo.
# - BUSINESS_UNIT: se restringe a los valores 'Mercado Libre', 'Mercado Pago' o 'Mercado Envíos'.
# - IS_EXTERNAL: se define como booleano, restringido a 0 o 1.
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USERNAME TEXT UNIQUE NOT NULL,
    START_DATE TEXT NOT NULL,
    END_DATE TEXT NULL,
    BUSINESS_UNIT TEXT NOT NULL CHECK(BUSINESS_UNIT IN ('Mercado Libre', 'Mercado Pago', 'Mercado Envíos')),
    MANAGER TEXT NOT NULL,
    LAST_UPDATE TEXT NOT NULL,
    IS_EXTERNAL BOOLEAN NOT NULL CHECK(IS_EXTERNAL IN (0,1))
)
''')

# 🔹 Crear la tabla "capacitaciones" si no existe
# Esta tabla guarda los datos de cada capacitación, incluyendo su nombre, enlace y fecha de creación.
cursor.execute('''
CREATE TABLE IF NOT EXISTS capacitaciones (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    LINK TEXT NOT NULL,
    CREATION_DATE TEXT NOT NULL
)
''')

# 🔹 Crear la tabla "capacitaciones_por_usuario" si no existe
# Esta tabla relaciona a los usuarios con las capacitaciones asignadas.
# Los campos FK_USERNAME y FK_TRAINING son claves foráneas que referencian a las tablas "usuarios" y "capacitaciones", respectivamente.
# Se utiliza ON DELETE CASCADE para que al eliminar un usuario o capacitación, se eliminen automáticamente los registros asociados.
cursor.execute('''
CREATE TABLE IF NOT EXISTS capacitaciones_por_usuario (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FK_USERNAME TEXT NOT NULL,
    FK_TRAINING INTEGER NOT NULL,
    END_DATE TEXT NULL,
    ASSIGNMENT_DATE TEXT NOT NULL,
    FOREIGN KEY (FK_USERNAME) REFERENCES usuarios(USERNAME) ON DELETE CASCADE,
    FOREIGN KEY (FK_TRAINING) REFERENCES capacitaciones(ID) ON DELETE CASCADE
)
''')

# 🔹 Crear la tabla "historico_kpis" si no existe
# Esta tabla almacenará los cálculos mensuales de las métricas:
# - Usuarios_Activos: porcentaje de usuarios activos.
# - Usuarios_Externos: porcentaje de usuarios externos activos.
# - Capacitaciones_Completadas: porcentaje de usuarios activos que han completado la capacitación.
# Se segmenta por BUSINESS_UNIT, restringido a los valores permitidos.
cursor.execute('''
CREATE TABLE IF NOT EXISTS historico_kpis (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Fecha TEXT NOT NULL,
    Usuarios_Activos REAL NOT NULL,
    Usuarios_Externos REAL NOT NULL,
    Capacitaciones_Completadas REAL NOT NULL,
    BUSINESS_UNIT TEXT NOT NULL CHECK(BUSINESS_UNIT IN ('Mercado Libre', 'Mercado Pago', 'Mercado Envíos'))
)
''')

# Guardar los cambios y cerrar la conexión con la base de datos.
conn.commit()
conn.close()

# Mensaje final para indicar que la base de datos se creó exitosamente.
print("[✅] Base de datos creada exitosamente")
