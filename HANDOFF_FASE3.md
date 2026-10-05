# Handoff — Fase 3

Este documento resume el estado validado del proyecto y el punto de arranque para Fase 3.

## Estado validado

- Fase 1 cerrada con CDMX como territorio operativo.
- Fase 2 implementada y verificada con PostgreSQL/PostGIS.
- Modelo dimensional en `sql/migrations/001_warehouse.sql`.
- Carga reproducible en `sql/etl/load_cdmx.sql` y `src/load_warehouse.py`.
- Vistas analíticas publicadas desde el DW en `sql/analytics/001_indicators.sql`.
- Validación local reportada: 23 pruebas, 18 checks de warehouse y 11 checks analíticos.

## Alcance espacial

- Unidad analítica: AGEB urbana.
- Entidad: Ciudad de México, clave 09.
- 2,431 polígonos válidos.
- Dos AGEB censales sin polígono quedan excluidas del análisis espacial hasta revisión.
- Regla actual de integración puntual: `intersects`; puntos ambiguos no se duplican.

## Fuentes activas

- Censo de Población y Vivienda 2020.
- Marco Geoestadístico 2020.
- DENUE noviembre 2020.
- FGJ: carpetas iniciadas en 2020. No interpretar como todos los hechos delictivos ocurridos en 2020.

Ver `docs/cdmx_acquisition.json`, `docs/plan_b_cdmx.md` y `docs/cierre_fase1.md`.

## Grain de hechos

- `fact_population`: una AGEB por dataset/edición censal.
- `fact_business_snapshot`: un establecimiento DENUE por snapshot.
- `fact_crime_record`: una fila publicada por FGJ por dataset.

## Vistas analíticas

- `analytics.kpi_ageb`
- `analytics.population_age_group`
- `analytics.incidents_by_type_time`

Los 14 KPIs requeridos se obtienen desde estas vistas. No consultar CSV/GeoDataFrames para métricas finales.

## Pendientes de Fase 3

1. Exploración de distribuciones y outliers de los KPIs.
2. Selección justificada de al menos tres relaciones y Pearson/Spearman según supuestos.
3. Construcción y documentación de pesos espaciales.
4. Global Moran's I para mínimo dos indicadores.
5. Local Moran's I / LISA para clusters y outliers espaciales.
6. Bivariate Moran's I o alternativa espacial justificada.
7. Mapas y figuras finales.
8. Interpretación: asociación espacial no implica causalidad.
9. Reporte técnico 4–6 páginas y presentación de máximo 5 pp.

## Reproducción resumida

1. Restaurar fuentes CDMX usando `src/restore_cdmx_sources.py` y verificar hashes.
2. Configurar `.env` y levantar PostGIS con Docker Compose.
3. Ejecutar migración/carga con `src/load_warehouse.py`.
4. Publicar vistas con `src/publish_analytics.py`.
5. Validar con `src/validate_warehouse.py` y `src/validate_analytics.py`.
6. Exportar análisis desde el DW mediante `src/export_analysis.py`.

## Cautelas

- No tratar ausencia de datos como cero.
- No agregar filas de distinto grain antes de agregar cada hecho por AGEB.
- No usar conteos FGJ sin conservar el significado temporal de “carpetas iniciadas en 2020”.
- Definir explícitamente la vecindad espacial y revisar componentes aislados.
- Si se usa normalización por población/área, documentar ceros y denominadores inválidos.
- Reportar significancia con pruebas de permutación cuando corresponda.
