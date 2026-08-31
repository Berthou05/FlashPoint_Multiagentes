# Diseño de la v1 de simulación

## Objetivo

Entregar una simulación autónoma del proyecto Flash Point con Mesa como fuente de verdad y Unity como cliente visual. Cada corrida usa una única estrategia de médico: reactiva/aleatoria o inteligente. La comparación estadística entre estrategias se realizará fuera de Unity y fuera del alcance de esta v1.

## Alcance funcional

- Tablero compartido de Mesa, con puertas y muros como límites entre celdas.
- Médicos de la peste con puntos de acción y turnos secuenciales.
- Pacientes, POIs, enjambres de ratas y rey rata en el tablero.
- Reglas de movimiento, apertura de puertas, daño a muros, tratamiento, recoger y soltar pacientes, rescates, muertes y daño estructural.
- Fase ambiental después de cada turno de médico, con las consecuencias de infestación definidas por el modelo.
- Dos configuraciones de estrategia:
  - `reactiva_aleatoria`, como línea base de decisiones simples o aleatorias.
  - `inteligente`, basada en tareas, riesgo/beneficio, costo de AP y planificación UCS/Dijkstra.
- Una corrida termina solo al alcanzar la condición de victoria o la condición de derrota establecida por las reglas. No se agrega un límite de turnos artificial.

## Arquitectura y flujo de datos

`plague_sim` concentra las reglas y el estado. `model.py` conserva el estado global y resuelve interacciones; `agents.py` decide y ejecuta acciones de los médicos; `entities.py` modela el estado simple de las entidades. La cuadrícula Mesa es la fuente de verdad espacial.

`server.py` crea, reinicia y avanza una corrida, y devuelve JSON con una representación estable del estado y eventos ordenados. Unity no replica reglas: solicita el estado al servidor y actualiza únicamente la representación visual.

## Unity incluido en la v1

La entrega incluye la preparación del proyecto Unity existente:

- Escena de tablero configurada.
- Assets existentes organizados y asignados a los prefabs necesarios.
- Prefabs o instanciación para médicos, pacientes/POIs, ratas, puertas, muros y marcadores de estado.
- Scripts de comunicación HTTP, deserialización de JSON, sincronización visual y controles de iniciar/reiniciar/avanzar o ejecutar.
- Interfaz con estrategia seleccionada, turno, médico/tarea o acción actual, AP, rescates, muertes, daño y estado terminal.

## Datos para evaluación posterior

Cada corrida conserva o exporta métricas mínimas: semilla/configuración, estrategia, rescates, muertes, daño estructural, cantidad de turnos ejecutados y resultado (victoria o derrota). Estas métricas se usarán después para comparar estrategias mediante varias corridas equivalentes.

## Criterios de aceptación de v1

1. Se puede seleccionar una estrategia y ejecutar una corrida completa hasta victoria o derrota.
2. Las entidades y reglas relevantes cambian en Mesa y Unity refleja esos cambios a través de JSON.
3. La estrategia inteligente selecciona tareas con utilidad y costos calculados; no usa una cadena fija de prioridades.
4. La estrategia reactiva/aleatoria también puede completar corridas bajo las mismas reglas.
5. Unity contiene escena, assets/prefabs y scripts configurados para observar la simulación sin contener la lógica del juego.
6. Las métricas de una corrida quedan disponibles para el análisis estadístico externo.
