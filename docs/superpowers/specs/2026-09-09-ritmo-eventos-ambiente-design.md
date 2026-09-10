# Ritmo visual de eventos de ambiente

## Objetivo

Mostrar de forma secuencial los cambios visuales que Mesa produce durante la
fase de ambiente, en lugar de mostrarlos todos en el mismo fotograma.

## Diseño

`SimulationRenderer` tendrá una duración configurable de `0.25` segundos para
eventos visuales del ambiente. Entre `environment_started` y `environment_ended`,
el renderizador aplicará cada evento y esperará esa duración solo después de un
cambio visible: infestación, POI, paciente, muro o puerta.

Los eventos técnicos y los movimientos de médicos no usan esta pausa. La
sincronización final mediante `RenderState` se conserva.

## Verificación

En Play Mode, una fase de ambiente debe mostrar cada cambio visible separado por
la pausa configurada y terminar con un tablero que coincide con el estado final
del servidor.
