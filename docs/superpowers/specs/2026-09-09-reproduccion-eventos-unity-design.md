# Reproducción ordenada de eventos en Unity

## Objetivo

Hacer que Unity represente cada cambio visual en el mismo orden en que Mesa lo
produce. Una puerta debe abrirse antes de que el médico la atraviese; las ratas,
POI y pacientes deben aparecer, desaparecer o cambiar antes del evento siguiente.

## Flujo

1. Python conserva la lista ordenada de eventos y el estado final de cada
   respuesta HTTP.
2. Los eventos que describen un límite incluyen las dos celdas que lo forman.
   Los eventos de entidades incluyen su identificador y posición cuando la
   entidad aparece o se retira.
3. `SimulationRenderer` reproduce cada evento en orden. Actualiza únicamente el
   objeto visual relacionado y espera la animación de movimiento cuando aplique.
4. Cuando termina la lista, `RenderState` sigue aplicando el estado final como
   sincronización de seguridad.

## Alcance

- Puertas: apertura, cierre y destrucción.
- Infestación: creación, eliminación y cambio entre RatSwarm y RatKing.
- POI: revelado o eliminación.
- Pacientes: creación, recogida, rescate y muerte.
- No se modifica la toma de decisiones, las reglas de Mesa ni el formato general
  de la respuesta HTTP.

## Manejo de inconsistencias

Si Unity no encuentra el objeto de un evento, escribe una advertencia y continúa.
El estado final reconstruye el objeto que deba existir, evitando que un fallo
visual bloquee el turno.

## Pruebas

- Pruebas de Python verifican que los eventos de puertas contienen sus celdas y
  conservan su secuencia.
- Las pruebas existentes de servidor verifican que la respuesta mantiene el
  orden de eventos.
- En Unity se valida de forma manual que una apertura de puerta se vea antes del
  movimiento del médico y que los cambios de ratas, POI y pacientes no esperen
  al final del turno.
