# Estado del tablero

El tablero es una cuadrícula Mesa de 8 por 10. Las entidades se colocan en celdas; muros y puertas se almacenan entre celdas en `boundaries`.

```mermaid
stateDiagram-v2
    [*] --> TableroCreado
    TableroCreado --> CeldasActivas: MultiGrid 8 x 10
    CeldasActivas --> ConPOI: colocar POI
    CeldasActivas --> ConPaciente: revelar POI con paciente
    CeldasActivas --> ConInfestacion: crear RatSwarm o RatKing
    ConPOI --> CeldasActivas: revelar o eliminar POI
    ConPaciente --> CeldasActivas: rescatar o matar paciente
    ConInfestacion --> CeldasActivas: eliminar infestación
    ConInfestacion --> ConInfestacion: evolucionar o propagar
```

Los cambios de los límites del tablero se detallan por separado en [Puertas y muros](./06-puertas-y-muros.md).
