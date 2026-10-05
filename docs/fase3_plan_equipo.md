# Fase 3 — implementación y reparto operativo

La Fase 3 queda implementada como módulos independientes para facilitar revisión, prueba y documentación por integrante. Todos los análisis consumen la exportación generada desde PostgreSQL/PostGIS mediante `src/export_analysis.py`; no calculan métricas finales desde los archivos raw.

## Reparto de revisión y responsabilidad

### Gael — base espacial y Global Moran
Archivos principales:
- `src/phase3_common.py`
- `src/phase3_global_moran.py`
- `src/phase3_run_all.py`

Responsabilidad de revisión: pesos Queen, islas/componentes, exclusión de NULL, reproducibilidad de permutaciones y Global Moran para dos indicadores.

### Esau — distribución y correlaciones
Archivos principales:
- `src/phase3_geographic_distribution.py`
- `src/phase3_correlations.py`

Responsabilidad de revisión: mapas descriptivos, selección de tres relaciones, justificación Pearson/Spearman, N efectivo, p-value y ausencia de lenguaje causal.

### Dalila — Local Moran / LISA
Archivo principal:
- `src/phase3_lisa.py`

Responsabilidad de revisión: clusters High–High, Low–Low, High–Low, Low–High; significancia por permutación; mapa LISA; islas y regla de vecindad.

### Josue — Bivariate Moran
Archivo principal:
- `src/phase3_bivariate_moran.py`

Responsabilidad de revisión: relación local X vs. lag espacial de Y, Bivariate Moran, significancia, scatterplot e interpretación no causal.

## Ejecución completa

1. Levantar y cargar el DW de acuerdo con el README.
2. Consultar el `dataset_id` activo con `python src/list_datasets.py`.
3. Exportar únicamente desde el DW:

```bash
python src/export_analysis.py --dataset-id <ID>
```

4. Ejecutar toda la Fase 3:

```bash
python src/phase3_run_all.py --dataset-id <ID> --permutations 999 --seed 42
```

Los resultados quedan en `outputs/cdmx/phase3/<ID>/`.

## Validaciones mínimas antes de entregar

- Al menos tres correlaciones con método justificado.
- Global Moran's I para mínimo dos indicadores.
- Local Moran / LISA con clusters y outliers espaciales.
- Una relación espacial bivariada.
- Regla de vecindad documentada: Queen contiguity.
- Islas/componentes reportados, no ocultados.
- Significancia mediante 999 permutaciones cuando corresponde.
- NULL excluidos explícitamente, nunca convertidos a cero para conservar N.
- Interpretación: asociación espacial y correlación no implican causalidad.

## Contribuciones en Git

Cada integrante debe ejecutar y revisar su módulo asignado, comprobar los resultados y realizar una contribución real identificable desde su propia cuenta (por ejemplo: corregir el código, documentar una decisión, añadir una validación o redactar la interpretación de los resultados obtenidos). No atribuir a una persona trabajo que no haya revisado o modificado realmente.
