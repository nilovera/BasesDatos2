# Medición de rendimiento

## Objetivo

Realizar una medición local y reproducible de operaciones simples sobre Redis para obtener una referencia del comportamiento del ambiente utilizado en el Hito 7.

## Entorno de prueba

- Procesador: Intel(R) Core(TM) 5 120U.
- Núcleos físicos: 10.
- Procesadores lógicos: 12.
- Memoria RAM: 13,7 GB.
- Sistema de contenedores: Docker Desktop sobre WSL2.
- Redis: 8.10.2 en modo standalone.
- Persistencia: AOF habilitado.
- Memoria máxima de Redis: 256 MB.
- Política de memoria: `noeviction`.

## Método

La prueba se ejecutó desde PowerShell mediante `redis-cli`, dentro del contenedor. Se utilizó una clave temporal llamada `contador:prueba:rendimiento`, con un TTL de 300 segundos.

Se midieron dos grupos de 10.000 operaciones:

1. Incrementos atómicos mediante `INCR`.
2. Lecturas mediante `GET`.

El tiempo total fue registrado con `Measure-Command`. La cantidad aproximada de operaciones por segundo se calculó dividiendo 10.000 por el tiempo total de cada prueba.

## Resultados

| Operación | Cantidad | Tiempo total | Rendimiento aproximado |
|---|---:|---:|---:|
| `INCR` | 10.000 | 24,357 segundos | 410,56 ops/s |
| `GET` | 10.000 | 2,903 segundos | 3.444,27 ops/s |

Al finalizar, el contador devolvió el valor `10000`. Esto confirma que todos los incrementos de la prueba fueron aplicados.

## Interpretación

Las lecturas resultaron más rápidas que los incrementos. `GET` solamente consulta el valor, mientras que `INCR` modifica el dato de forma atómica. Además, el ambiente tiene AOF habilitado, por lo que las escrituras forman parte del mecanismo de persistencia configurado.

Los resultados incluyen el costo de ejecutar `docker exec`, iniciar `redis-cli` y procesar su salida. Por lo tanto, representan una medición local de extremo a extremo y no el rendimiento máximo aislado del servidor Redis. Tampoco deben extrapolarse directamente a un ambiente productivo.

## Conclusión

La prueba permite verificar que Redis atiende correctamente operaciones de lectura e incremento en el ambiente del proyecto. También demuestra que `INCR` conserva la exactitud del contador, ya que las 10.000 operaciones produjeron el valor final esperado.
