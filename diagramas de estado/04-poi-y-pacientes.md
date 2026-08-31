# Estados de POI y pacientes

Un POI conserva si oculta un paciente. Al revelarse, se elimina del tablero; solo crea un paciente cuando `has_patient` es verdadero.

```mermaid
stateDiagram-v2
    [*] --> POIOculto
    POIOculto --> POIVacioRetirado: revelar POI vacío
    POIOculto --> PacienteEnTablero: revelar POI con paciente
    POIOculto --> PacienteMuerto: RatKing llega y el POI tenía paciente
    POIOculto --> POIVacioRetirado: RatKing llega y el POI era vacío
    PacienteEnTablero --> PacienteRescatado: rescue_patient()
    PacienteEnTablero --> PacienteMuerto: RatKing llega a su celda
    PacienteRescatado --> [*]
    PacienteMuerto --> [*]
    POIVacioRetirado --> [*]
```

La recogida y el transporte por un médico están planeados, pero todavía no existen como acciones implementadas.
