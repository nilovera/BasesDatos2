# Fixture 2030 — Capacidad, SLO y recuperación

## Definiciones y criterio de medición

Un SLI es una medición, como latencia p95, proporción de errores o edad de un
mensaje. Un SLO establece un objetivo para un indicador y una ventana. Un SLA
es un compromiso de servicio con condiciones acordadas; el proyecto no posee
un SLA contractual de producción.

El throughput es la cantidad de solicitudes completadas por segundo. La
concurrencia es el número de operaciones o clientes simultáneos. No son valores
intercambiables. En un régimen estable, la relación L≈λW permite razonar sobre
concurrencia, tasa y tiempo medio, sin sustituir la medición de percentiles.

La capacidad se evalúa con volumen de datos, distribución de claves, proporción
lectura/escritura y duración. El pico de una final puede concentrarse en un
partido, por lo que una carga uniforme no representa ese riesgo.

## Objetivos y resultados del laboratorio

| Aspecto | Objetivo del perfil | Resultado y alcance |
|---|---|---|
| Humo | Aproximadamente 2 req/s; cero errores, p95 ≤750 ms y p99 ≤1.500 ms | Ejecución corregida y de recuperación aprobadas |
| Normal | 20 req/s, 12 clientes virtuales, tres repeticiones de 60 s | 19,998 req/s, 3.600 solicitudes, cero errores y p95 34,926 ms |
| Estrés | 80 req/s, 40 clientes virtuales, 60 s | 79,932 req/s, 4.800 solicitudes, cero errores y p95 55,110 ms; resultado informativo |
| Frescura Outbox | Observar profundidad y edad; alerta local sobre retraso | Convergencia y replay comprobados en una falla controlada; sin distribución de latencia extremo a extremo a gran volumen |
| Disponibilidad | Detectar caída y recuperación | Fallas locales registradas; sin porcentaje anual de disponibilidad |
| Data Mart | Comparar resultados y latencia con la fuente operacional | Dos comparaciones pequeñas y carga mixta ejecutadas; sin generalización de escala |

La primera prueba de humo incumplió latencia y se conserva como diagnóstico.
Los resultados corregidos no la reemplazan ni la ocultan. Los cuatro perfiles
posteriores suman 8.460 solicitudes sin errores. La prueba de estrés alcanzó
cerca de 80 req/s; no midió el punto de saturación ni demuestra capacidad
máxima sostenida.

## Recuperación: RPO y RTO

RPO es la pérdida de datos tolerable, expresada como distancia temporal respecto
del último punto recuperable. RTO es el tiempo objetivo para restablecer el
servicio. La confirmación transaccional y la persistencia por volumen reducen
ciertos riesgos, pero no acreditan por sí solas valores de RPO/RTO.

Las pruebas existentes detienen un contenedor, observan la alerta y lo reinician
sin eliminar su volumen. No simulan pérdida del host ni restauración desde una
copia externa. En consecuencia, el proyecto no declara RPO cero ni un RTO
productivo medido. Esos objetivos deben acordarse y comprobarse con un ensayo
que identifique inicio, recuperación funcional y datos recuperados.

## Procedimiento de evaluación

1. Identificar commit, equipo, estado de datos, semilla y perfil.
2. Verificar salud y registrar conteos antes de la carga.
3. Medir tasa solicitada y lograda, errores, p50/p95/p99 y recursos.
4. Conservar las repeticiones y los resultados desfavorables.
5. Comparar igualdad funcional antes de atribuir una ventaja de rendimiento.
6. Ejecutar una comprobación posterior para detectar degradación residual.

Los scripts conservan muestras de CPU y memoria por contenedor. El porcentaje
de CPU Docker puede superar 100 % cuando utiliza varios núcleos. No se
interpreta ese valor como un porcentaje normalizado de todo el equipo.

## Cobertura y extensiones

La carga actual es de lectura mixta. Para evaluar escritura social o auditoría
se necesita otro perfil con reintentos, claves calientes, tamaño de partición
y confirmación durable. La auditoría tiene validación unitaria y comprobación
HTTP real registrada con resultado OK. Ese recorrido funcional no mide capacidad
de escritura, particiones calientes ni fallas de replicación.

Una evaluación de escala requiere aumentar datos y duración, repetir en
condiciones comparables, buscar saturación y verificar recuperación. La alta
disponibilidad requiere pruebas con réplicas reales y fallas de sus dominios.
Estas extensiones no invalidan las mediciones locales ya realizadas, pero
delimitan las conclusiones que puede sostener el proyecto.

Evidencias: [estado de validación](../estado_validacion.md).
Protocolo ejecutable: [pruebas de carga](../rendimiento/pruebas_carga_sla_slo.md).
