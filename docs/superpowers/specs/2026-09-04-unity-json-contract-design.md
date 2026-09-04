# Contrato JSON v1 orientado a Unity

## Objetivo

Sustituir la respuesta HTTP actual, que expone estructuras internas de Python,
por el contrato JSON v1 acordado para que Unity pueda deserializar, identificar
objetos y reproducir animaciones sin transformar listas de posiciones ni
interpretar valores `null`.

## Límite del cambio

Mesa continúa siendo la única fuente de verdad. No se cambian las reglas del
tablero ni la toma de decisiones de los médicos. El cambio afecta cómo se
asignan IDs a muros y puertas, cómo el modelo exporta estado y eventos, y cómo
Unity solicita las fases HTTP.

## Respuesta común

Todas las respuestas exitosas de simulación usarán exactamente:

```json
{
  "api_version": "v1",
  "state_version": 0,
  "events": [],
  "state": {}
}
```

Se elimina el envoltorio previo `status` y `game_state`. `GET /state` no
incrementa `state_version`; `/reset` lo fija en 0; `/step_doctor` y
`/step_environment` lo incrementan una vez después de completar su fase.

## Estado exportado

`state` siempre incluye las claves descritas por el documento de API:
`width`, `height`, `turn`, `phase`, `active_doctor_id`, `game_status`,
`house_damage`, `patients_rescued`, `patients_killed`, `strategy`,
`doctors`, `rat_swarms`, `rat_kings`, `pois`, `patients`, `walls` y `doors`.

Las entidades del tablero exportan `id`, `x` y `y`. Muros y puertas exportan
`id`, `ax`, `ay`, `bx`, `by` y sus campos de estado. Los pares de celdas de
los límites conservan la llave canónica de `model.boundaries`; se les asigna
un ID persistente al crearlos, sin duplicar sus coordenadas dentro de las
entidades.

No se emite `null`: `active_doctor_id` y `carried_patient_id` usan `-1` cuando
no existe una entidad activa o cargada. `game_status` es siempre `running`,
`victory` o `defeat`. Las listas existen aun cuando estén vacías.

## Eventos

Cada evento conserva `sequence` y `type`; los datos se exportan con los
nombres Unity del contrato. Los movimientos usan `id`, `from_x`, `from_y`,
`to_x`, `to_y` y `action_points` restante. Creaciones, eliminaciones y cambios
de entidades usan `id`, `x`, `y` cuando corresponda. Los límites usan su ID
persistente. La promoción de una rata conserva explícitamente
`rat_swarm_id` y `rat_king_id`.

Los eventos siguen siendo un registro ordenado de una fase completa; `state`
es el snapshot final y autoritativo tras esa fase.

## Responsabilidades

- `model.py` conserva reglas y posiciones Mesa, emite eventos semánticos y
  ofrece una exportación plana del estado.
- `server.py` valida solicitudes, controla `state_version` y devuelve el
  envoltorio uniforme. No reimplementa reglas de juego.
- Unity deserializa el contrato, reproduce `events` por `sequence` y usa
  `state` para sincronizar la escena. Su URL por defecto apunta al puerto
  `8585` del servidor Python.

## Pruebas de aceptación

1. Reset, consulta de estado y las dos fases retornan solo las cuatro claves
   superiores del contrato.
2. Ninguna respuesta de simulación contiene `null`.
3. `state_version` sigue la secuencia 0, 1, 2 para reset, doctor y ambiente.
4. Las coordenadas del snapshot y de eventos se exponen como enteros planos.
5. Cada muro y puerta tiene un ID estable durante la corrida.
6. Los eventos se mantienen ordenados y el snapshot coincide con el estado
   final del modelo.
