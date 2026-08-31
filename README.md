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

Tests will be added later when the first game mechanics are implemented.


