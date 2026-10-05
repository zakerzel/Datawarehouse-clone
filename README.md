# DataHauseWare

Proyecto de BI — Unidad 2: Data Warehouse geoespacial reproducible.

Territorio operativo: **Ciudad de México (CDMX)**, con AGEB urbanas como unidad analítica.

## Objetivo

Integrar información demográfica, económica, geográfica y de seguridad pública para calcular KPIs territoriales y analizar relaciones espaciales desde un Data Warehouse en PostgreSQL/PostGIS.

## Fuentes

- INEGI Censo de Población y Vivienda 2020.
- INEGI Marco Geoestadístico 2020.
- INEGI DENUE noviembre 2020.
- FGJ CDMX, carpetas de investigación iniciadas en 2020.

Las fuentes, URLs, hashes y ediciones se documentan en `docs/cdmx_acquisition.json`.

## Pipeline

RAW -> CLEAN -> SPATIAL JOIN -> POSTGRESQL/POSTGIS DW -> ANALYTICS

## Fase 1

La integración territorial usa AGEB urbanas de CDMX. Los puntos DENUE y FGJ se convierten a geometrías y se asignan a polígonos mediante reglas reproducibles. La evidencia y decisiones están en `docs/cierre_fase1.md`, `docs/decision_geografica.md` y `docs/validacion_geografica.md`.

## Fase 2

Modelo dimensional y ETL implementados en PostgreSQL/PostGIS:

- `sql/migrations/001_warehouse.sql`
- `sql/etl/load_cdmx.sql`
- `sql/analytics/001_indicators.sql`
- `src/load_warehouse.py`
- `src/validate_warehouse.py`
- `src/validate_analytics.py`

Las vistas analíticas generan los KPIs desde el warehouse, no directamente desde archivos raw.

## Documentos clave

- [Bitácora](BITACORA.md)
- [Handoff de Fase 3](HANDOFF_FASE3.md)
- [Modelo y ETL de Fase 2](docs/fase2_modelo_etl.md)
- [Cierre de Fase 1](docs/cierre_fase1.md)

## Ejecutar la comprobación geográfica

Python 3.12. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe src/assess_geography.py --config config/cdmx.json
.\.venv\Scripts\python.exe src/assess_crime_cdmx.py
```

## PostgreSQL/PostGIS

```powershell
Copy-Item .env.example .env
# Editar POSTGRES_PASSWORD en .env con una contraseña local.
docker compose up -d db
docker compose exec db psql -U urban -d urban_intelligence -c "SELECT PostGIS_Version();"
```

Ver `HANDOFF_FASE3.md` para continuar con análisis espacial.
