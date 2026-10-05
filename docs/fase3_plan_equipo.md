# Fase 3 — plan de trabajo del equipo

La Fase 1 y la Fase 2 se toman como baseline validado. La Fase 3 se desarrolla en ramas separadas para que cada integrante aporte cambios técnicos reales y revisables.

## Regla común

Todo análisis final debe consumir el Data Warehouse o la exportación producida por `src/export_analysis.py`. No calcular KPIs finales desde archivos raw. Para cada análisis se deben documentar variables, exclusiones, tamaño de muestra, regla espacial, significancia e interpretación.

## División

### Gael — infraestructura espacial + Global Moran's I
Rama: `phase3/gael-spatial-foundation`

- Dependencias de estadística espacial.
- Loader reproducible de `kpi_ageb.csv` + `areas.geojson`.
- Auditoría de valores faltantes y topología.
- Pesos Queen y reporte de islas/componentes.
- Global Moran's I para al menos dos indicadores.
- Moran scatterplots y resumen JSON.
- Integración final de Fase 3 y revisión de reproducibilidad.

### Esau — exploración y correlaciones
Rama: `phase3/esau-correlations`

- Explorar distribuciones y outliers de KPIs candidatos.
- Elegir al menos tres relaciones justificadas.
- Determinar Pearson o Spearman según distribución/supuestos.
- Reportar coeficiente, p-value, N y exclusiones.
- Generar tres figuras interpretables.
- Evitar lenguaje causal.

### Dalila — Local Moran / LISA
Rama: `phase3/dalila-lisa`

- Reutilizar la misma definición de vecindad acordada.
- Local Moran's I para indicadores seleccionados.
- Identificar High–High, Low–Low, High–Low y Low–High.
- Filtrar clusters por significancia de permutación.
- Generar LISA cluster maps y tabla/resumen de clusters.
- Documentar islas y sensibilidad de la vecindad.

### Josue — Bivariate Moran + visualización
Rama: `phase3/josue-bivariate`

- Seleccionar una relación bivariada con sentido analítico.
- Calcular Bivariate Moran's I con pruebas de permutación.
- Explicar qué significa comparar una variable local con el lag espacial de otra.
- Generar scatter/mapa o visualización complementaria.
- Preparar figuras finales con fuente, periodo, unidad y leyendas.

## Después de las cuatro ramas

1. Revisar y fusionar PRs.
2. Ejecutar Fase 3 completa desde un clon limpio.
3. Seleccionar mapas/figuras finales para versionar.
4. Completar diagrama dimensional y data dictionary final.
5. Actualizar README con reproducción de Fase 3.
6. Redactar reporte técnico de 4–6 páginas.
7. Preparar presentación de máximo 5 páginas/slides.

## Criterios de interpretación

- Asociación/correlación no implica causalidad.
- Los resultados espaciales dependen de la regla de vecindad.
- No convertir NULL a cero solo para conservar observaciones.
- FGJ representa carpetas iniciadas en 2020 bajo la regla candidate-v1; no equivale automáticamente a incidencia delictiva real.
- Reportar el número de observaciones efectivas después de exclusiones.
