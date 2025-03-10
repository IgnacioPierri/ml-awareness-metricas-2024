import sqlite3
import pandas as pd
from datetime import datetime, date
import calendar

# Ruta de la base de datos (se asume que ya fue creada con setup_db.py)
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'database.db')


def calcular_metricas():
    """
    Recorre cada mes del 2024 y para cada Unidad de Negocio (BU), calcula las métricas mensuales:
      - Porcentaje de usuarios activos.
      - Porcentaje de usuarios externos (activo) dentro de la BU.
      - Porcentaje de capacitaciones completadas (de usuarios activos) hasta ese mes.
    
    Estos cálculos se basan en datos acumulativos hasta el **último día del mes** (para reflejar la actividad completa).
    Los resultados se insertan en la tabla 'historico_kpis' para su posterior análisis.
    """
    # Abrir conexión con la base de datos
    conn = sqlite3.connect(DB_PATH)
    
    # Definir las unidades de negocio según lo especificado
    unidades_negocio = ["Mercado Libre", "Mercado Pago", "Mercado Envíos"]

    # ------------------------------------------------------------------------------
    # Generar una lista de fechas (como cadenas) para el **último día** de cada mes del 2024.
    # Se utiliza calendar.monthrange para obtener el número de días de cada mes.
    # Por ejemplo, para enero: calendar.monthrange(2024, 1) retorna (weekday, 31), luego se genera "2024-01-31".
    # ------------------------------------------------------------------------------
    meses = []
    for mes in range(1, 13):
        ultimo_dia = calendar.monthrange(2024, mes)[1]  # Obtiene el último día del mes
        fecha = date(2024, mes, ultimo_dia)
        meses.append(fecha.strftime("%Y-%m-%d"))

    # ------------------------------------------------------------------------------
    # Para cada fecha (representando el último día del mes) y para cada BU, se calculan las métricas.
    # ------------------------------------------------------------------------------
    for mes in meses:
        for unidad in unidades_negocio:
            # Consultar el total de usuarios en la BU que hayan iniciado la capacitación en o antes de 'mes'
            total_users = pd.read_sql(f"""
                SELECT COUNT(*) as total FROM usuarios 
                WHERE BUSINESS_UNIT = '{unidad}' AND START_DATE <= '{mes}'
            """, conn).iloc[0]["total"]

            # Si no hay usuarios para la BU en ese mes, se guarda 0 en todos los indicadores
            if total_users == 0:
                guardar_historico(mes, unidad, 0, 0, 0)
                continue  # Pasar a la siguiente iteración

            # Consultar el número de usuarios activos en la BU para 'mes'
            # Un usuario se considera activo si:
            #  - No tiene fecha de finalización (END_DATE IS NULL) o
            #  - Su fecha de finalización es posterior o igual a 'mes'
            # Además, se incluyen solo aquellos usuarios que hayan iniciado en o antes de 'mes'.
            activos = pd.read_sql(f"""
                SELECT COUNT(*) as activos FROM usuarios 
                WHERE BUSINESS_UNIT = '{unidad}' 
                  AND (END_DATE IS NULL OR END_DATE >= '{mes}')
                  AND START_DATE <= '{mes}'
            """, conn).iloc[0]["activos"]

            # Calcular el porcentaje de usuarios activos respecto al total
            porcentaje_activos = (activos / total_users) * 100

            # Consultar el número de usuarios externos activos en la BU, con la misma lógica de actividad.
            externos_activos = pd.read_sql(f"""
                SELECT COUNT(*) as externos FROM usuarios 
                WHERE BUSINESS_UNIT = '{unidad}' AND IS_EXTERNAL = 1 
                  AND (END_DATE IS NULL OR END_DATE >= '{mes}')
                  AND START_DATE <= '{mes}'
            """, conn).iloc[0]["externos"]

            porcentaje_externos = (externos_activos / total_users) * 100

            # Consultar el número de usuarios (únicos, por eso se usa COUNT(DISTINCT ...)) que han completado
            # alguna capacitación hasta 'mes', considerando solo a los usuarios activos.
            # Se realiza un JOIN entre 'capacitaciones_por_usuario' y 'usuarios' para obtener la BU y la condición de actividad.
            completadas = pd.read_sql(f"""
                SELECT COUNT(DISTINCT cu.FK_USERNAME) as completadas 
                FROM capacitaciones_por_usuario cu
                JOIN usuarios u ON cu.FK_USERNAME = u.USERNAME
                WHERE u.BUSINESS_UNIT = '{unidad}' 
                  AND cu.END_DATE <= '{mes}'
                  AND (u.END_DATE IS NULL OR u.END_DATE >= '{mes}')
            """, conn).iloc[0]["completadas"]

            # Calcular el porcentaje de capacitaciones completadas respecto a los usuarios activos.
            porcentaje_completadas = (completadas / activos) * 100 if activos > 0 else 0

            # Insertar el registro de métricas en la tabla 'historico_kpis'
            guardar_historico(mes, unidad, porcentaje_activos, porcentaje_externos, porcentaje_completadas)

    # Cerrar la conexión a la base de datos
    conn.close()
    print("[✅] Métricas calculadas correctamente.")

def guardar_historico(fecha, business_unit, activos, externos, completadas):
    """
    Inserta un registro en la tabla 'historico_kpis' con los valores calculados.
    
    Parámetros:
      - fecha: La fecha (último día del mes) para la que se calcula la métrica.
      - business_unit: La unidad de negocio correspondiente.
      - activos: Porcentaje de usuarios activos.
      - externos: Porcentaje de usuarios externos activos.
      - completadas: Porcentaje de capacitaciones completadas (de usuarios activos).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO historico_kpis (Fecha, Usuarios_Activos, Usuarios_Externos, Capacitaciones_Completadas, BUSINESS_UNIT)
    VALUES (?, ?, ?, ?, ?)
    ''', (fecha, activos, externos, completadas, business_unit))
    
    conn.commit()
    conn.close()
    print(f"[✅] Datos guardados para {business_unit} en {fecha}")

# Ejecutar la función principal si se corre este script directamente
if __name__ == "__main__":
    calcular_metricas()
