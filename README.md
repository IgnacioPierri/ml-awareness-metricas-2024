# Meli Awareness - Métricas 2024

Este proyecto es una solución para el challenge de automatización de métricas para el equipo de Awareness Security de Mercado Libre. La aplicación consume datos de estado de capacitaciones (internos y externos) desde una base de datos relacional, calcula mensualmente el porcentaje de finalización de las capacitaciones de ciberseguridad (tomando solo en cuenta a los usuarios activos) por cada Unidad de Negocio (BU) y despliega un dashboard interactivo con Streamlit para facilitar su análisis.

## Características

- **Automatización de métricas:**  
  Se recorren los datos de usuarios y capacitaciones para calcular, para cada mes del año, el porcentaje de usuarios activos, de usuarios externos (dentro de los activos) y el porcentaje de capacitaciones completadas (de los usuarios activos).

- **Dashboard interactivo:**  
  Visualización de:
  - Resumen mensual (tabla pivot) con los porcentajes acumulados hasta el cierre de cada mes.
  - Gráficos de evolución mensual del porcentaje de capacitaciones completadas.
  - Comparación de la proporción de usuarios activos internos vs. externos.
  - Gráficos individuales por cada Unidad de Negocio.
  - Ranking de BU según el porcentaje promedio de capacitaciones completadas a lo largo del año.
  - Sección con datos crudos para ver la integridad de los datos.

- **Elementos adicionales:**  
  En el sidebar se incluye un filtro por BU, una sección "Acerca de" con enlace a mi [LinkedIn](https://www.linkedin.com/in/ignacio-pierri/) y un botón interactivo que muestra un aviso de seguridad al acceder a un link externo para ver ataques en tiempo real.

## Estructura del Proyecto

El proyecto se compone de los siguientes scripts:

- **setup_db.py:**  
  Crea la base de datos SQLite y define las tablas `usuarios`, `capacitaciones`, `capacitaciones_por_usuario` y `historico_kpis`.

- **generar_datasets.py:**  
  Utiliza Faker para generar un dataset ficticio de 200 usuarios, las capacitaciones y los registros de capacitaciones por usuario.

- **calcular_metricas.py:**  
  Recorre los datos para cada mes del 2024 (calculando hasta el último día de cada mes) y cada BU, y calcula:
  - Porcentaje de usuarios activos.
  - Porcentaje de usuarios externos activos.
  - Porcentaje de capacitaciones completadas (de usuarios activos).  
  Los resultados se insertan en la tabla `historico_kpis`.

- **dashboard.py:**  
  Es el dashboard de Streamlit que consume la información de `historico_kpis` (y otros datos para análisis adicional) para visualizar:
  - Resumen mensual (tabla pivot).
  - Gráfico de evolución mensual.
  - Distribución de usuarios activos: internos vs. externos.
  - Gráficos individuales por BU.
  - Ranking de BU según el promedio anual de capacitaciones completadas.

## Instrucciones para Ejecutar el Proyecto

1. **Clonar el repositorio:**  
   
    git clone https://github.com/IgnacioPierri/ml-awareness-metricas-2024
    cd ml-awareness-metricas-2024


2. **Instalar dependencias:**  
    
    pip install -r requirements.txt

3. **Configurar la base de datos:**  
Ejecuta el script setup_db.py para crear la base de datos y las tablas:
    
    python setup_db.py

4. **Generar los datos ficticios:**  
Ejecuta generar_datasets.py para insertar los datos en la base de datos:

    python generar_datasets.py

5. **Calcular las métricas:**  
Ejecuta calcular_metricas.py para procesar los datos y llenar la tabla historico_kpis:
    
    python calcular_metricas.py

6. **Ejecutar el dashboard:**  
Finalmente, lanza el dashboard con Streamlit:
    
    streamlit run dashboard.py
    
## Consideraciones y Mejoras

- **Cálculo de Métricas:**  
  Las métricas se calculan de forma acumulativa hasta el **último día de cada mes** para reflejar la actividad completa del período. Solo se consideran los usuarios activos (es decir, aquellos que no tienen fecha de finalización o cuya fecha de finalización es posterior al mes evaluado).

- **Dashboard Profesional:**  
  Se han incorporado visualizaciones interactivas, filtros, análisis comparativos y un ranking que destaca las BU con mayor y menor adopción de capacitaciones. Esto permite a los responsables identificar rápidamente tendencias y áreas de mejora.

- **Manejo de Errores y Documentación:**  
  El código está ampliamente comentado para facilitar su comprensión. Se recomienda mantener la modularización para facilitar el mantenimiento y la escalabilidad.

## Credenciales de Acceso a la Plataforma de ETL

En esta solución se utiliza una base de datos SQLite local, por lo que no se requieren credenciales de acceso a una plataforma ETL externa. Sin embargo, la solución puede adaptarse para integrarse con plataformas como DataFlow, Pentaho o Apache NiFi, según las necesidades del proyecto.

## Contacto

Si tienes alguna duda o sugerencia, no dudes en contactarme a través de mi [LinkedIn](https://www.linkedin.com/in/ignacio-pierri/).

---

¡Gracias por revisar este proyecto!
