# Estado del juego

Este diagrama representa el ciclo que ejecuta actualmente `PlagueSimulationModel`.

```mermaid
stateDiagram-v2
    [*] --> Inicializacion
    Inicializacion --> TurnoActivo: modelo creado
    TurnoActivo --> FaseEntorno: advance_turn()
    FaseEntorno --> RevisarFinal: infestacion, POI y evolucion
    RevisarFinal --> Victoria: 7 pacientes rescatados
    RevisarFinal --> Derrota: 4 pacientes muertos
    RevisarFinal --> Derrota: daño de casa >= 24
    RevisarFinal --> TurnoActivo: sin condición final
    Victoria --> [*]
    Derrota --> [*]
```

En el código actual, `advance_turn()` incrementa el turno y ejecuta la fase de entorno. La activación secuencial de los médicos es comportamiento propuesto para la siguiente etapa.
