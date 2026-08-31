# Estados de la infestación

La infestación comienza en una celda vacía como `RatSwarm`. Una nueva infestación en esa misma celda la convierte en `RatKing`; una nueva infestación sobre un RatKing inicia un brote.

```mermaid
stateDiagram-v2
    [*] --> CeldaSinInfestacion
    CeldaSinInfestacion --> RatSwarm: add_infestation()
    RatSwarm --> RatKing: nueva infestación
    RatSwarm --> RatKing: adyacente a RatKing pasable
    RatKing --> Brote: nueva infestación
    Brote --> RatSwarm: alcanza celda vacía
    Brote --> RatKing: alcanza RatSwarm
    Brote --> Brote: atraviesa RatKing
    RatSwarm --> CeldaSinInfestacion: remove_infestation()
    RatKing --> CeldaSinInfestacion: remove_infestation()
```

Durante un brote, un límite bloqueante recibe daño. Un muro destruido permite continuar el brote; una puerta destruida absorbe esa dirección del brote.
