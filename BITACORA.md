# Bitácora de DataHauseWare

Última actualización: 2026-10-03 (America/Mexico_City).

Este es el punto de entrada para retomar el proyecto entre sesiones. Mantener el estado actual arriba y agregar una entrada al historial al terminar cada sesión de trabajo. Registrar solo acciones realizadas y distinguirlas de propuestas. No guardar contraseñas ni datos personales.

## Retomar en dos minutos

- **Carpeta:** `C:\Users\IGNITER\Downloads\DataHauseWare`.
- **Territorio activo:** CDMX; el usuario activó Plan B porque el trámite de seguridad de Mérida rebasa el plazo. El profesor no es proveedor de datos.
- **Fase:** 1 cerrada; Fase 2 implementada y validada localmente, lista para revisión del PR. Modelo y guía en docs/fase2_modelo_etl.md y HANDOFF_FASE3.md.
- **Configuración:** `config/cdmx.json`; usar siempre `--config config/cdmx.json` para el evaluador geográfico (su valor por defecto conserva Mérida).
- **Resultados:** 2,431 polígonos válidos; 472,608 registros DENUE y 194,356 registros FGJ asignados. Seguridad: 9,111 coordenadas inválidas/ausentes y 654 filas fuera.
- **Límites:** dos AGEB censales sin polígono (7,108 habitantes); FGJ es cohorte de inicio 2020, no todos los hechos de 2020. Precisión, elegibilidad y cobertura pendientes. No interpretar todos los registros como delitos.
- **Siguiente acción:** usuario crea PR de codex/fase-2-modelo-etl-postgis hacia main, revisar CI y reproducir la guía en otro equipo; después análisis de Fase 3. PR aún no creado automáticamente por preferencia del usuario.
- **Guía vigente y contrato:** [Plan B](docs/plan_b_cdmx.md). [Manifiesto](docs/cdmx_acquisition.json).
- **Validación:** 23 pruebas aprobadas (9 integración), 18 controles DW y 11 analíticos; cero superposiciones de AGEB. Selección operativa candidate-v1: 199,650 candidatos FGJ, 191,233 asignados; competencia desconocida conservada y marcada.
- **PostGIS:** activo; DW cargado (dataset local 2), vistas publicadas, repetición sin duplicados y paridad fila a fila comprobada. Consultar list_datasets.py; no asumir ID 2 en otro equipo.
- **No rehacer:** originales y resultados de Mérida se conservan; originales CDMX ya descargados. No mezclar territorios ni inventar coordenadas. Los documentos de Mérida son antecedentes, no evidencia activa de CDMX.

## Decisiones vigentes

1. Alcance: AGEB urbanas de entidad 09; no toda la zona metropolitana ni zonas rurales. Dos claves sin geometría quedan explícitamente excluidas del diagnóstico espacial hasta revisión.
2. Periodo operativo: Censo/Marco 2020, DENUE 11/2020, carpetas iniciadas 2020; referencias temporales distintas documentadas.
3. Conservar originales, URLs, hashes, fechas y rechazos. Ausencia de datos no equivale a cero.
4. `_id` de FGJ identifica una fila del DataStore; no garantiza unicidad de carpeta. Conservar filas repetidas por atributos hasta aclaración.
5. Un repositorio para todas las fases y contribuciones reales. Los KPIs finales se calcularán desde el DW.

## Dónde encontrar cada cosa

- [README](README.md): instalación y comandos.
- [Arquitectura](docs/arquitectura.md): propuesta de granularidad, adaptación de seguridad y validaciones.
- [Configuración activa CDMX](config/cdmx.json) y [Mérida histórica](config/merida.json).
- `data/raw/`: originales. No modificarlos ni volver a descargarlos sin motivo.
- [Recolector inicial](src/download_inegi.py): todavía específico de Yucatán.
- [Evaluación geográfica](src/assess_geography.py) y [motor espacial](src/spatial.py).
- `outputs/merida/phase1/`: diagnóstico JSON, asignaciones, resumen por AGEB, GeoJSON y mapa.
- [Mapa de comprobación](outputs/merida/phase1/spatial_check.png).
- Enunciado original, fuera del repositorio: `D:\Downloads\Unit 2 - Project.pdf`.

Datos, entorno y salidas regenerables están ignorados por Git; la bitácora y los manifiestos sí deben versionarse. La carpeta temporal de preparación en el otro espacio de trabajo no es la fuente del proyecto: editar siempre DataHauseWare.

## Rutina de continuidad

Al comenzar una sesión: leer esta bitácora, revisar el estado real de los archivos y de Git, incorporar novedades del usuario y tomar el primer pendiente viable. Las instrucciones del usuario más recientes prevalecen sobre esta nota.

Al terminar: actualizar estado y siguiente acción; agregar una entrada fechada con cambios, comprobaciones, decisiones y pendientes. Conservar entradas anteriores; corregir datos erróneos con una nota explícita. No repetir pruebas ya aprobadas salvo cambios relevantes o dudas nuevas. No marcar completa la Fase 1 sin la evidencia que falta.

## Historial

### 2026-09-29 — Recolección y estructura inicial

- Se revisó el enunciado y se eligió evaluar AGEB urbanas de Mérida.
- Se descargaron Censo 2020, diccionario, Marco Geoestadístico 2020 y DENUE mayo 2026 de INEGI, con manifiestos y hashes.
- Se investigaron CEISP, SESNSP y fuentes municipales. No se confirmó microdato local con coordenadas; fallos de acceso a CEISP no prueban que los datos no existan.
- Se creó estructura configurable, entorno Python, motor espacial, pruebas, Compose y documentación.
- Se ejecutó la integración: 483 AGEB, 921,771 habitantes y 54,925 negocios asignados; discrepancias pendientes 141+7.
- Tres pruebas pasaron. Compose aceptó la configuración; el contenedor no se ejecutó porque el servicio Docker no estaba activo. No hay warehouse poblado.

### 2026-09-29 — Bitácora de continuidad

- A petición del usuario, se creó este archivo y se enlazó desde README.
- Se cotejó el estado con README, validación geográfica y estado Git. No se modificaron datos, lógica de procesamiento ni resultados.
- Siguiente sesión: comenzar por la revisión de discrepancias espaciales y continuar con variables de KPIs; incorporar novedades sobre seguridad si las hay.

### 2026-09-29 — Auditoría espacial de continuidad

- Se retomó la bitácora y se comprobó el estado Git; no se hicieron commits ni cambios en datos originales.
- Se creó y ejecutó `src/audit_discrepancies.py`, configurable por territorio y con verificación de hashes contra el diagnóstico previo.
- Los 141 exteriores están a menos de 500 m; 89 a 100 m o menos. En 64 la clave AGEB declarada no aparece en la capa urbana 2020; seis caen en otra AGEB urbana del estado.
- Los siete interiores con otras claves declaran Kanasín (1), Umán (2), La Roca (3) y Progreso (1). Se conservaron señalados y sin corrección.
- Se verificaron 148 identificadores únicos, conciliación 141+7 y distancias cero al área en los siete interiores. Cero pares de polígonos con intersección de superficie positiva.
- Reporte: `docs/auditoria_discrepancias.md`. Evidencia por registro y resumen en `outputs/merida/phase1/discrepancy_audit.csv` y `.json`.
- No se repitieron las tres pruebas previas: el motor de asignación no cambió. No se demostró la causa exacta de las discrepancias ni ausencia de huecos cartográficos.
- Siguiente acción: diccionario de variables/KPIs y perfil de faltantes; seguridad y decisión temporal siguen pendientes.

### 2026-09-29 — Gestión presencial de datos de seguridad

- El usuario visitó su estación de policía cercana; según informó, le indicaron acudir a la sede central ubicada por Periférico.
- No se recibieron archivos ni confirmación de que exista una base georreferenciada accesible para el proyecto.
- El usuario estima informalmente 60% de posibilidad de que exista la información y 30% de que exista y se la proporcionen. Son expectativas personales, no probabilidades verificadas ni criterios técnicos de decisión.
- Seguridad sigue pendiente. No se contactó a ninguna institución desde este proyecto.
- El próximo trabajo técnico permanece: diccionario de variables para KPIs y perfil de faltantes/denominadores; CDMX sigue como alternativa sin activar.

### 2026-09-29 — Diccionario y perfil de insumos para KPIs

- Se contrastaron variables con los diccionarios originales de los ZIP y la estructura sectorial del INEGI.
- Creados `src/profile_kpi_inputs.py` y `docs/diccionario_kpis.md`; README enlaza el comando y el documento.
- Perfil ejecutado con verificación de hashes/configuración: cinco AGEB con población cero, once sin negocios asignados, símbolos `*` en variables censales y 24 empates de sector dominante.
- Los estratos DENUE de personal ocupado no son conteos exactos de empleos. PEA usa 12+ como denominador propuesto. Faltantes no se convierten a cero y los grupos de edad no deben superponerse.
- Siguiente acción: cerrar o descartar seguridad; evaluar comparabilidad temporal y verificar formalmente SCIAN antes de calcular KPIs finales.

### 2026-09-30 — Cambio de territorio a CDMX y ejecución de Plan B

- El usuario indicó que el plazo del proyecto no permite esperar datos de seguridad de Mérida y activó CDMX como territorio operativo.
- Se descargaron Censo 2020, Marco Geoestadístico 2020, DENUE noviembre 2020 y FGJ 2020 para CDMX y se registraron fuentes/hashes en `docs/cdmx_acquisition.json`.
- Se ejecutó el evaluador geográfico con `config/cdmx.json`: 2,431 AGEB urbanas válidas; 472,608 registros DENUE asignados; 194,356 FGJ asignados; 9,111 coordenadas inválidas/ausentes; 654 fuera.
- Se implementaron y ejecutaron auditoría de cobertura, calidad de FGJ y sensibilidad espacial; se registraron reportes JSON/Markdown.
- Se definió candidate-v1 para seguridad con reglas reproducibles y sin inventar coordenadas.
- Se mantuvieron Mérida y sus outputs como antecedentes históricos, no como evidencia activa.

### 2026-10-01 — Fase 2 Data Warehouse PostGIS

- Se creó el modelo dimensional en `sql/migrations/001_warehouse.sql` y carga reproducible en `sql/etl/load_cdmx.sql`.
- Se añadieron `src/database.py`, `src/load_warehouse.py`, `src/validate_warehouse.py`, `src/compare_dw_phase1.py` y pruebas de integración.
- Se levantó PostgreSQL/PostGIS con Docker, se cargó el DW y se verificó idempotencia y paridad con resultados de Fase 1.
- Se publicaron vistas analíticas en `sql/analytics/001_indicators.sql` y se verificaron los 14 KPIs requeridos.
- Resultado local: 23 pruebas aprobadas, 18 controles DW y 11 analíticos.
- Fase 2 considerada implementada y lista para revisión externa.
