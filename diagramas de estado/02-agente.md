# Estado del agente

El manejo de puntos de acción y fin de turno ya existe. La selección automática de tareas aún es una propuesta: `PlagueDoctorAgent.step()` no tiene comportamiento implementado.

```mermaid
stateDiagram-v2
    [*] --> Creado
    Creado --> InicioTurno: start_turn()
    InicioTurno --> Disponible: 4 puntos de acción
    Disponible --> Disponible: acción válida y PA suficiente
    Disponible --> FinTurno: sin PA o end_turn()
    FinTurno --> InicioTurno: siguiente turno del médico

    state "Decisión propuesta" as Propuesta {
        [*] --> Observar
        Observar --> GenerarTareas
        GenerarTareas --> CalcularCosto
        CalcularCosto --> ElegirUtilidad
        ElegirUtilidad --> EjecutarPlan
    }
    Disponible --> Propuesta: comportamiento futuro
```

Las acciones propuestas usan los costos centralizados en `PlagueDoctorAgent.ACTION_COSTS`.
