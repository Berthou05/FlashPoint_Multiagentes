using System;

// Guarda la información básica de los doctores
[Serializable]
public class DoctorData
{
    public int id;

    // Posición del doctor dentro del tablero
    public int x;
    public int y;

    // Puntos de acción que todavía tiene disponibles
    public int action_points;

    // -1 significa que no está cargando ningún paciente
    public int carried_patient_id;
}


// Esta clase sirve para las entidades que solo necesitan ID y posición.
// Por ejemplo: RatSwarm, RatKing, POI y Patient.
[Serializable]
public class EntityData
{
    public int id;
    public int x;
    public int y;
}


// Información de cada muro del tablero
[Serializable]
public class WallData
{
    public int id;

    // Las dos casillas que divide el muro
    public int ax;
    public int ay;
    public int bx;
    public int by;

    // Cuánto daño ha recibido
    public int damage;

    // Indica si el muro ya fue destruido
    public bool destroyed;
}


// Información de cada puerta
[Serializable]
public class DoorData
{
    public int id;

    // Las dos casillas que conecta la puerta
    public int ax;
    public int ay;
    public int bx;
    public int by;

    // Estado actual de la puerta
    public bool open;
    public bool destroyed;
}


// Representa una acción que ocurrió durante la simulación.
// No todos los eventos utilizan todos estos datos.
// Los campos que no se usen simplemente llegan con su valor por defecto.
[Serializable]
public class SimulationEvent
{
    // Orden en el que Unity debe reproducir los eventos
    public int sequence;

    // Nos dice qué ocurrió, por ejemplo:
    // doctor_moved, door_opened, wall_damaged, etc.
    public string type;

    // ID de la entidad relacionada con el evento
    public int id;

    // Algunos eventos pueden involucrar una segunda entidad
    public int other_id;

    // Posición sencilla, usada por eventos como outbreak_started
    public int x;
    public int y;

    // Posición inicial y final para movimientos o propagaciones
    public int from_x;
    public int from_y;
    public int to_x;
    public int to_y;

    // Coordenadas de muros o puertas si algún evento las necesita
    public int ax;
    public int ay;
    public int bx;
    public int by;

    // Datos adicionales que pueden cambiar durante un evento
    public int action_points;
    public int damage;
}


// Este es el estado completo del juego después de que ocurrieron los eventos
[Serializable]
public class SimulationState
{
    // Tamaño del tablero
    public int width;
    public int height;

    // Información del turno actual
    public int turn;
    public string phase;
    public int active_doctor_id;

    // running, victory o defeat
    public string game_status;

    // Contadores generales de la partida
    public int house_damage;
    public int patients_rescued;
    public int patients_killed;

    // Estrategia que está utilizando la simulación
    public string strategy;

    // Todos los elementos que existen actualmente en el tablero
    public DoctorData[] doctors;

    public EntityData[] rat_swarms;
    public EntityData[] rat_kings;
    public EntityData[] pois;
    public EntityData[] patients;

    public WallData[] walls;
    public DoorData[] doors;
}


// Esta clase sirve como molde para guardar todo el JSON que manda Python

[Serializable]
public class SimulationResponse
{
    // Nos permite saber qué versión de la API estamos usando
    public string api_version;

    // Cambia cada vez que la simulación avanza
    public int state_version;

    // Acciones que ocurrieron para llegar al nuevo estado
    public SimulationEvent[] events;

    // Estado completo después de terminar esas acciones
    public SimulationState state;
}