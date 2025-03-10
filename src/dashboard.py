import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------------------------------------------
# Se configura la aplicación de Streamlit:
# - Título de la pestaña.
# - Favicon (icono) de Mercado Libre.
# - Layout "wide" para aprovechar el ancho de la pantalla.
st.set_page_config(
    page_title="Meli Awareness - Métricas 2024",
    page_icon="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg",
    layout="wide"
)

# ------------------------------------------------------------------------------
# TÍTULO PRINCIPAL Y DESCRIPCIÓN
# ------------------------------------------------------------------------------
st.title("📊 Meli Awareness - Métricas 2024")

st.markdown("""
### 📡 Seguimiento de capacitaciones de ciberseguridad en Mercado Libre

En este dashboard podrás visualizar:
- El **porcentaje de finalización** de las capacitaciones de ciberseguridad.
- La **evolución** de dichas capacitaciones a lo largo del año (de forma acumulativa, calculada al cierre de cada mes).
- Una **segmentación** por cada Unidad de Negocio (BU): Mercado Libre, Mercado Pago y Mercado Envíos.
""")

# ------------------------------------------------------------------------------
# CONEXIÓN A LA BASE DE DATOS Y CARGA DE DATOS
# ------------------------------------------------------------------------------
# Se conecta a la base de datos y se cargan los datos de:
# - 'historico_kpis': contiene las métricas calculadas mensualmente.
# - 'usuarios', 'capacitaciones' y 'capacitaciones_por_usuario': datos crudos para análisis adicional.
DB_PATH = "../db/database.db"
conn = sqlite3.connect(DB_PATH)

df_historico = pd.read_sql("""
    SELECT Fecha, BUSINESS_UNIT, 
           Usuarios_Activos,
           Usuarios_Externos,
           Capacitaciones_Completadas
    FROM historico_kpis 
    ORDER BY Fecha, BUSINESS_UNIT
""", conn)

df_usuarios = pd.read_sql("SELECT * FROM usuarios", conn)
df_capacitaciones = pd.read_sql("SELECT * FROM capacitaciones", conn)
df_capacitaciones_por_usuario = pd.read_sql("SELECT * FROM capacitaciones_por_usuario", conn)

conn.close()

st.markdown("---\n")

# ------------------------------------------------------------------------------
# SIDEBAR: FILTROS Y BRANDING
# ------------------------------------------------------------------------------
st.sidebar.header("Filtros")
business_units = ["Mercado Libre", "Mercado Pago", "Mercado Envíos"]
selected_bu = st.sidebar.multiselect("Selecciona la Unidad de Negocio", business_units, default=business_units)

st.sidebar.markdown("---")
st.sidebar.markdown("#### Acerca de")
st.sidebar.info(
    "Proyecto de automatización de métricas de capacitación en ciberseguridad.\n\n"
    "Desarrollado por [Ignacio Pierri](https://www.linkedin.com/in/ignacio-pierri/)."
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### **¿Es importante la ciberseguridad?**")
if st.sidebar.button("Ver ataques en tiempo real"):
    st.sidebar.info("⚠️ Recordá siempre [verificar](https://www.virustotal.com/gui/url/e6c2fcd26992568ddcfb3363052903a1c497275bb1ccf0075fdc883a1bcd78b7) el link al que estás accediendo.")
    st.sidebar.markdown(
        '[Haz clic aquí para ver ataques en tiempo real en Threat Map de Check Point](https://threatmap.checkpoint.com/)',
        unsafe_allow_html=True
    )




# ------------------------------------------------------------------------------
# FILTRADO Y FORMATEO DE LOS DATOS
# ------------------------------------------------------------------------------
df = df_historico.copy()
if not df.empty:
    df = df[df["BUSINESS_UNIT"].isin(selected_bu)]

if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.strftime("%b %Y")  # Ejemplo: "Jan 2024"
    
    # Mapeo para traducir los nombres de los meses al español.
    meses_map = {
        "Jan": "Ene", "Feb": "Feb", "Mar": "Mar", "Apr": "Abr",
        "May": "May", "Jun": "Jun", "Jul": "Jul", "Aug": "Ago",
        "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Dec": "Dic"
    }
    df["Mes"] = df["Mes"].apply(lambda x: x.replace(x.split()[0], meses_map[x.split()[0]]))
    
    # Definir el orden cronológico de los meses para 2024 (de Ene a Dic)
    meses_ordenados = [f"{meses_map[datetime(2024, m, 1).strftime('%b')]} 2024" for m in range(1, 13)]
    df["Mes"] = pd.Categorical(df["Mes"], categories=meses_ordenados, ordered=True)
    df.sort_values("Mes", inplace=True)


# ------------------------------------------------------------------------------
# 1️⃣ TABLA RESUMEN GENERAL
# ------------------------------------------------------------------------------
st.subheader("📄 Resumen Mensual de Capacitaciones (Todas las BUs)")
st.markdown("""
Esta tabla muestra el **porcentaje de capacitaciones completadas** en cada mes, discriminado por Unidad de Negocio. Los valores se calculan de forma acumulativa hasta el cierre del mes.
""")
if df.empty:
    st.warning("⚠️ No hay datos en el histórico. Ejecuta calcular_metricas.py primero.")
else:
    df_pivot = df.pivot_table(index="Mes", columns="BUSINESS_UNIT", values="Capacitaciones_Completadas", aggfunc="mean")
    df_pivot = df_pivot.reindex(meses_ordenados)
    df_pivot.columns = [f"{col}" for col in df_pivot.columns]
    with st.expander("🔍 Ver detalles de la tabla general", expanded=True):
        st.dataframe(df_pivot.style.format("{:.2f}%"))

st.markdown("---\n")

# ------------------------------------------------------------------------------
# 2️⃣ GRÁFICO GENERAL DE EVOLUCIÓN
# ------------------------------------------------------------------------------
st.subheader("📈 Evolución Mensual del Porcentaje de Capacitaciones Completadas")
st.markdown("""
Este gráfico muestra la evolución del **porcentaje de colaboradores activos que han completado la capacitación de ciberseguridad** a lo largo de los meses para cada BU. Un incremento sostenido indica una mayor adopción de las iniciativas de ciberseguridad.
""")
if not df.empty:
    fig, ax = plt.subplots(figsize=(12, 6))
    for bu in df["BUSINESS_UNIT"].unique():
        df_bu = df[df["BUSINESS_UNIT"] == bu]
        ax.plot(df_bu["Mes"], df_bu["Capacitaciones_Completadas"], marker="o", linestyle="-", label=bu)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Porcentaje de Capacitaciones Completadas (%)")
    ax.legend(title="Unidad de Negocio", loc="upper left", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No hay datos para mostrar el gráfico.")

st.markdown("---\n")

# ------------------------------------------------------------------------------
# 3️⃣ DISTRIBUCIÓN GENERAL POR BU: ACTIVOS INTERNOS vs. EXTERNOS
# ------------------------------------------------------------------------------
st.subheader("📊 Proporción de Usuarios Activos: Internos vs. Externos")
st.markdown("""
A continuación se muestra la proporción (en %) de usuarios activos que son **internos** versus aquellos que son **externos** (colaboradores contratados de proveedores) para cada Unidad de Negocio. Cada barra representa el 100% de los usuarios activos, dividida en la parte inferior (internos) y la parte superior (externos).
""")
if not df.empty:
    # Agrupar por BU y calcular el promedio de usuarios activos y externos (valor ya calculado en % respecto al total de usuarios)
    df_group = df.groupby("BUSINESS_UNIT")[["Usuarios_Activos", "Usuarios_Externos"]].mean()
    # Calcular el porcentaje de usuarios internos (dentro de los activos) como:
    #   (Usuarios_Activos - Usuarios_Externos) / Usuarios_Activos * 100
    df_group["Usuarios_Internos"] = (df_group["Usuarios_Activos"] - df_group["Usuarios_Externos"]) / df_group["Usuarios_Activos"] * 100
    # Recalcular el porcentaje de externos dentro del total de usuarios activos
    df_group["Usuarios_Externos"] = (df_group["Usuarios_Externos"] / df_group["Usuarios_Activos"]) * 100
    # Seleccionar solo las dos columnas que nos interesan (cada fila debe sumar 100% si Usuarios_Activos > 0)
    df_proporcion = df_group[["Usuarios_Internos", "Usuarios_Externos"]]
    
    # Plot de gráfico de barras apiladas, cada barra suma 100%
    fig, ax = plt.subplots(figsize=(10, 5))
    df_proporcion.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    ax.set_ylabel("Porcentaje (%)")
    ax.set_xlabel("Unidad de Negocio")
    ax.set_title("Proporción de Usuarios Activos: Internos vs. Externos")
    ax.legend(loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)
else:
    st.info("No hay datos para mostrar la distribución.")

st.markdown("---\n")

# ------------------------------------------------------------------------------
# 4️⃣ GRÁFICOS POR UNIDAD DE NEGOCIO
# ------------------------------------------------------------------------------
st.subheader("📊 Evolución de Capacitaciones por Unidad de Negocio")
st.markdown("""
A continuación, se presenta un **gráfico de línea** individual para cada BU, mostrando el **porcentaje de capacitaciones completadas** a lo largo de los meses. Esto facilita la comparación y la detección de brechas o picos en cada unidad.
""")
if not df.empty:
    for unidad in df["BUSINESS_UNIT"].unique():
        st.markdown(f"**{unidad}**")
        df_unidad = df[df["BUSINESS_UNIT"] == unidad]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df_unidad["Mes"], df_unidad["Capacitaciones_Completadas"], marker="o", linestyle="-", color="red")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Porcentaje de Capacitaciones Completadas (%)")
        ax.set_title(f"Capacitaciones completadas - {unidad}")
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig)
else:
    st.info("No hay datos para mostrar los gráficos por BU.")

st.markdown("---\n")

# ------------------------------------------------------------------------------
# 5️⃣ SECCIÓN: DATOS CRUDOS
# ------------------------------------------------------------------------------
st.subheader("📑 Datos Crudos de la Base de Datos")
st.markdown("""
En esta sección se muestran los **registros en crudo** de cada tabla, lo cual es útil para verificar la integridad de los datos y para análisis adicionales.
""")
with st.expander("Ver datos crudos de 'usuarios'", expanded=False):
    st.dataframe(df_usuarios)
with st.expander("Ver datos crudos de 'capacitaciones'", expanded=False):
    st.dataframe(df_capacitaciones)
with st.expander("Ver datos crudos de 'capacitaciones_por_usuario'", expanded=False):
    st.dataframe(df_capacitaciones_por_usuario)
st.markdown("---\n")
st.subheader("📑 Datos Crudos de 'historico_kpis' (completos)")
with st.expander("Ver datos crudos de 'historico_kpis'", expanded=False):
    st.dataframe(df_historico)

st.markdown("---\n")

# ------------------------------------------------------------------------------
# 6️⃣ NUEVA SECCIÓN: RANKING DE UNIDADES DE NEGOCIO
# ------------------------------------------------------------------------------
st.subheader("🏆 Ranking de Unidades de Negocio")
st.markdown("""
A continuación se muestra el **ranking** de las unidades de negocio según el **porcentaje promedio** de capacitaciones completadas (a lo largo del año, calculado con los datos históricos). Esto permite identificar cuál BU ha logrado una mayor adopción de las iniciativas de ciberseguridad.
""")
if not df_historico.empty:
    # Se calcula el promedio anual de "Capacitaciones_Completadas" por BU utilizando la tabla histórica completa.
    ranking = df_historico.groupby("BUSINESS_UNIT")["Capacitaciones_Completadas"].mean().sort_values(ascending=False)
    # Formatear los valores para mostrarlos como porcentaje con 2 decimales.
    ranking_formateado = ranking.apply(lambda x: f"{x:.2f}%")
    st.write(ranking_formateado)
    
    # Se identifica la BU con el mayor y el menor promedio.
    top_bu = ranking.idxmax()
    bottom_bu = ranking.idxmin()
    top_value = ranking[top_bu]
    bottom_value = ranking[bottom_bu]
    
    st.markdown(f"**La unidad de negocio con mayor porcentaje promedio de capacitaciones completadas es: {top_bu} ({top_value:.2f}%).**")
    st.markdown(f"**La unidad de negocio con menor porcentaje promedio de capacitaciones completadas es: {bottom_bu} ({bottom_value:.2f}%).**")
else:
    st.info("No hay datos para calcular el ranking.")

st.markdown("---\n")

# ------------------------------------------------------------------------------
# PIE DE PÁGINA: BRANDING
# ------------------------------------------------------------------------------
st.markdown(
    "<div style='text-align: center;'>"
    "Desarrollado por <strong>Ignacio Pierri</strong>"
    "</div>", 
    unsafe_allow_html=True
)

st.success("✅ Dashboard actualizado con éxito.")
