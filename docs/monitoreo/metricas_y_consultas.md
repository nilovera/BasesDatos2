# Metricas y consultas PromQL

Prometheus recolecta cada 5 segundos. Las ventanas siguientes son decisiones
de laboratorio y deben conservarse junto con la fecha, commit y escenario de
cada ejecucion.

## Disponibilidad de la API

```promql
up{job="fixture2030-api"}
```

- Unidad: booleano (`1` disponible, `0` no disponible).
- Periodo: ultimo scrape, con frecuencia de 5 segundos.
- Uso: panel de disponibilidad y alerta `Fixture2030ApiDown`.

## Latencia p95

```promql
histogram_quantile(0.95, sum by (le) (rate(fixture2030_http_request_duration_seconds_bucket[5m])))
```

- Unidad: segundos.
- Periodo: ventana movil de 5 minutos.
- Uso: observar la latencia del 95 % de las solicitudes sin confundirla con un
  promedio. Solo sera un resultado medido despues de ejecutar un escenario.

## Volumen de solicitudes

```promql
sum(rate(fixture2030_http_requests_total[1m]))
```

- Unidad: solicitudes por segundo.
- Periodo: ventana movil de 1 minuto.
- Uso: correlacionar carga con latencia y errores.

## Proporcion de errores 5xx

```promql
sum(rate(fixture2030_http_requests_total{status=~"5.."}[2m]))
/
clamp_min(sum(rate(fixture2030_http_requests_total[2m])), 0.001)
```

- Unidad: proporcion entre 0 y 1; multiplicar por 100 para porcentaje.
- Periodo: ventana movil de 2 minutos.
- Uso: alerta de tasa de error superior al 5 %.
