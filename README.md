# FlashPoint_Multiagentes
## Plague Point - Multiagentes

## Diagramas de estado

Los diagramas de estado requeridos para la entrega se encuentran en la carpeta [`diagramas de estado`](./diagramas%20de%20estado/). Los comportamientos marcados como **propuestos** representan la siguiente etapa del proyecto; no están implementados todavía en `PlagueDoctorAgent.step()`.

- [Estado del juego](./diagramas%20de%20estado/01-juego.md)
- [Estado del agente](./diagramas%20de%20estado/02-agente.md)
- [Estado del tablero](./diagramas%20de%20estado/03-tablero.md)
- [Estados de POI y pacientes](./diagramas%20de%20estado/04-poi-y-pacientes.md)
- [Estados de la infestación](./diagramas%20de%20estado/05-infestacion.md)
- [Estados de puertas y muros](./diagramas%20de%20estado/06-puertas-y-muros.md)
- [Acciones y estados del médico de la peste](./diagramas%20de%20estado/07-acciones-del-medico.md)


### File structure

```
FlashPoint_Multiagentes/
├── server.py              # HTTP bridge between Unity and the simulation
├── requirements.txt       # Python dependencies
├── plague_sim/
│   ├── __init__.py
│   ├── model.py           # board, rules, turns, infestation and game state
│   ├── agents.py          # PlagueDoctorAgent behaviour and decisions
│   └── entities.py        # patients, encounters, walls, doors and rats
└── LICENSE
```

La suite de pruebas vive en `tests/` y cubre las reglas básicas, las fases y
los endpoints HTTP.

## API v1

Inicia el servidor con `python server.py` en el puerto `8585`. Las respuestas
de simulación tienen esta forma:

```json
{
  "api_version": "v1",
  "status": "...",
  "events": [],
  "game_state": {}
}
```

Endpoints disponibles:

- `GET /state`: devuelve el snapshot actual. Si aún no existe un modelo, crea
  el estado inicial.
- `POST /reset`: reinicia el modelo. Acepta `strategy`, `num_agents` y `seed`.
- `POST /step_doctor`: ejecuta exactamente una acción del Doctor activo.
- `POST /step_environment`: ejecuta toda la fase ambiental.
- `POST /step_complete_turn`: termina las acciones restantes del Doctor y
  ejecuta la fase ambiental.
- `POST /step`: alias de `/step_complete_turn`.

`game_state.phase` puede ser `doctor`, `environment` o `finished`. El campo
`turn` cuenta únicamente turnos completos terminados. Unity debe reproducir
`events` por `sequence` y usar `game_state` como snapshot final.


