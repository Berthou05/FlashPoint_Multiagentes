# Estados de puertas y muros

Muros y puertas viven entre dos celdas. Un límite solo es atravesable cuando su propiedad `is_passable` es verdadera.

## Puerta

```mermaid
stateDiagram-v2
    [*] --> Cerrada
    Cerrada --> Abierta: open()
    Abierta --> Cerrada: close()
    Cerrada --> Destruida: take_damage()
    Abierta --> Destruida: take_damage()
    Destruida --> [*]
```

Una puerta destruida queda abierta al paso y añade 2 puntos al daño de la casa.

## Muro

```mermaid
stateDiagram-v2
    [*] --> Intacto
    Intacto --> Dañado: primer take_damage()
    Dañado --> Destruido: segundo take_damage()
    Destruido --> [*]
```

Un muro destruido queda abierto al paso. Cada impacto añade 1 punto al daño de la casa.
