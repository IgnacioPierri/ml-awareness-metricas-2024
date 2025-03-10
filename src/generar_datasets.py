import sqlite3
import random
from faker import Faker
from datetime import date

# Ruta de la base de datos (se espera que ya exista la base creada con setup_db.py)
DB_PATH = "../db/database.db"

# Instanciar Faker para generar datos ficticios
fake = Faker()

# ----------------------------------------------------------------------
# Función: generar_usuarios(n)
# ----------------------------------------------------------------------
def generar_usuarios(n):
    """
    Genera un conjunto de 'n' usuarios ficticios con fechas coherentes de inicio y finalización.
    
    Cada usuario es una tupla con los siguientes campos:
      - USERNAME: Nombre de usuario único.
      - START_DATE: Fecha de inicio (entre el 1 de enero y 31 de diciembre de 2024).
      - END_DATE: Fecha de finalización; se asigna con una probabilidad del 50%.
                  Si no se asigna, se considera que el usuario sigue activo.
      - BUSINESS_UNIT: Unidad de negocio, elegida aleatoriamente entre 'Mercado Libre',
                       'Mercado Pago' y 'Mercado Envíos'.
      - MANAGER: Se genera otro nombre de usuario aleatorio para simular el manager.
      - LAST_UPDATE: Fecha de la última actualización, entre la fecha de inicio y el 31 de diciembre de 2024.
      - IS_EXTERNAL: Valor booleano (True/False) asignado aleatoriamente, para indicar si es un usuario externo.
      
    Se utiliza un conjunto (set) para evitar duplicados en el USERNAME.
    """
    # Lista de unidades de negocio disponibles
    unidades = ["Mercado Libre", "Mercado Pago", "Mercado Envíos"]
    # Utilizamos un set para evitar duplicados (cada elemento es una tupla)
    users = set()
    
    # Generar usuarios hasta alcanzar el número deseado
    while len(users) < n:
        username = fake.user_name()
        # Verificar si el username ya fue generado (evitar duplicados)
        if username in [u[0] for u in users]:
            continue
        
        # Generar una fecha de inicio aleatoria dentro de 2024
        start_date = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 12, 31))
        # Con 50% de probabilidad asignar una fecha de finalización (que sea entre start_date y fin de 2024)
        end_date = None if random.random() > 0.5 else fake.date_between(start_date=start_date, end_date=date(2024, 12, 31))
        # Generar una fecha de última actualización entre el start_date y fin de 2024
        last_update = fake.date_between(start_date=start_date, end_date=date(2024, 12, 31))
        
        # Agregar al conjunto el usuario como tupla formateando las fechas a cadena "YYYY-MM-DD"
        users.add((
            username,
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d") if end_date else None,
            random.choice(unidades),
            fake.user_name(),  # Simula el manager
            last_update.strftime("%Y-%m-%d"), 
            random.choice([True, False])  # Indica si es usuario externo
        ))
    return list(users)

# ----------------------------------------------------------------------
# Función: generar_capacitaciones()
# ----------------------------------------------------------------------
def generar_capacitaciones():
    """
    Retorna una lista de tuplas, cada una representando una capacitación.
    
    Cada tupla contiene:
      - NAME: Nombre de la capacitación.
      - LINK: URL asociada a la capacitación.
      - CREATION_DATE: Fecha de creación del curso.
      
    Se definen 3 capacitaciones: Ciberseguridad, Código de Ética y Onboarding.
    """
    return [
        ("Ciberseguridad", "https://meli.ciberseguridad.training.com", "2023-12-01"),
        ("Código de Ética", "https://meli.etica.training.com", "2023-12-03"),
        ("Onboarding", "https://meli.onboarding.training.com", "2022-10-10")
    ]

# ----------------------------------------------------------------------
# Función: generar_capacitaciones_por_usuario(users)
# ----------------------------------------------------------------------
def generar_capacitaciones_por_usuario(users):
    """
    Genera registros de capacitaciones asignadas a cada usuario.
    
    Para cada usuario se generan entre 1 y 3 registros, simulando que un usuario puede
    tener asignado uno o varios cursos.
    
    Cada registro es una tupla que contiene:
      - FK_USERNAME: El username del usuario (clave foránea a la tabla 'usuarios').
      - FK_TRAINING: Un número entero aleatorio entre 1 y 3 que indica el ID de la capacitación asignada.
      - END_DATE: Fecha en la que se completó la capacitación, con una probabilidad del 70% de asignarse.
                  Si no se asigna, se deja como None, indicando que no se completó la capacitación.
      - ASSIGNMENT_DATE: Se asigna la fecha de inicio del usuario, simulando que la capacitación se asigna en el inicio.
    """
    rows = []
    for user in users:
        # Convertir la fecha de inicio (cadena) a objeto date
        start_date = date.fromisoformat(user[1])
        # Generar entre 1 y 3 registros de capacitación para cada usuario
        for _ in range(random.randint(1, 3)):
            # Con probabilidad del 70% se asigna una fecha de finalización (entre el start_date y el 31 de diciembre de 2024)
            end_date = fake.date_between(start_date=start_date, end_date=date(2024, 12, 31)) if random.random() > 0.3 else None
            rows.append((
                user[0],  # FK_USERNAME
                random.randint(1, 3),  # FK_TRAINING (valor entre 1 y 3, correspondiendo a las capacitaciones generadas)
                end_date.strftime("%Y-%m-%d") if end_date else None,  # Fecha de finalización (si existe)
                start_date.strftime("%Y-%m-%d")  # ASSIGNMENT_DATE: se usa la fecha de inicio del usuario
            ))
    return rows

# ----------------------------------------------------------------------
# Función: insertar_datos()
# ----------------------------------------------------------------------
def insertar_datos():
    """
    Inserta los datos ficticios generados en la base de datos.
    
    - Genera 200 usuarios.
    - Genera las capacitaciones predefinidas.
    - Genera los registros de capacitaciones por usuario.
    
    Luego, inserta estos datos en las tablas correspondientes:
      - 'usuarios'
      - 'capacitaciones'
      - 'capacitaciones_por_usuario'
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generar datos
    usuarios = generar_usuarios(200)
    capacitaciones = generar_capacitaciones()
    capacitaciones_por_usuario = generar_capacitaciones_por_usuario(usuarios)

    # Insertar datos en la tabla 'usuarios'
    cursor.executemany('''
    INSERT INTO usuarios (USERNAME, START_DATE, END_DATE, BUSINESS_UNIT, MANAGER, LAST_UPDATE, IS_EXTERNAL)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', usuarios)

    # Insertar datos en la tabla 'capacitaciones'
    cursor.executemany('''
    INSERT INTO capacitaciones (NAME, LINK, CREATION_DATE)
    VALUES (?, ?, ?)
    ''', capacitaciones)

    # Insertar datos en la tabla 'capacitaciones_por_usuario'
    cursor.executemany('''
    INSERT INTO capacitaciones_por_usuario (FK_USERNAME, FK_TRAINING, END_DATE, ASSIGNMENT_DATE)
    VALUES (?, ?, ?, ?)
    ''', capacitaciones_por_usuario)

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    print("[✅] Datos ficticios insertados en la base de datos")

# Ejecutar la inserción de datos si se corre el script directamente
if __name__ == "__main__":
    insertar_datos()
