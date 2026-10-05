# Fase 3 — guía de ejecución e interpretación

## Objetivo

Evaluar patrones y relaciones espaciales entre indicadores demográficos, económicos y de seguridad pública a nivel AGEB urbana de CDMX.

## 1. Distribución geográfica

Se generan mapas de `population_density`, `business_density` y `crime_records_per_1000`. Los mapas son descriptivos: permiten observar heterogeneidad territorial, pero no prueban asociación estadística ni causalidad.

## 2. Correlaciones

Relaciones predeterminadas:

1. Population density vs. business density.
2. Population density vs. crime records per 1,000 residents.
3. Business density vs. crime records per 1,000 residents.

La selección Pearson/Spearman es reproducible: Spearman se usa si alguna variable tiene |skew| > 1 o más de 5% de outliers por la regla IQR; en caso contrario se usa Pearson. Se reportan coeficiente, p-value, N y exclusiones.

## 3. Pesos espaciales

Se utiliza Queen contiguity: dos AGEB son vecinas si comparten borde o vértice. La matriz se estandariza por fila. Se reportan islas, componentes y número de vecinos; las islas no se conectan artificialmente mediante KNN.

## 4. Global Moran's I

Se calcula para `crime_records_per_1000` y `business_density` con 999 permutaciones. Un resultado significativo indica autocorrelación espacial global, no una relación causal.

## 5. Local Moran / LISA

Se calculan patrones locales para los mismos indicadores. Solo observaciones con `p_sim < 0.05` reciben una etiqueta de cluster:

- High–High: valor alto rodeado por valores altos.
- Low–Low: valor bajo rodeado por valores bajos.
- High–Low: valor alto rodeado por valores bajos; posible outlier espacial.
- Low–High: valor bajo rodeado por valores altos; posible outlier espacial.

## 6. Bivariate Moran

La relación predeterminada compara `business_density` local con el lag espacial de `crime_records_per_1000` de AGEB vecinas. El estadístico indica asociación espacial entre variables distintas; no implica que los negocios causen delitos ni viceversa.

## 7. Precaución sobre seguridad pública

Los registros FGJ representan carpetas iniciadas en 2020 bajo la regla operacional del proyecto. `crime_records_per_1000` debe interpretarse como una razón de registros analíticos del dataset y no como una medida perfecta de riesgo delictivo real.
