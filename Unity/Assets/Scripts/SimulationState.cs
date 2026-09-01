using System;

[Serializable]
public class PositionData
{
    public int x;
    public int y;
}

[Serializable]
public class DoctorData
{
    public int id;
    public PositionData position;
    public int action_points;
    public string strategy;
    public int carried_patient_id;
}

[Serializable]
public class EntityData
{
    public int id;
    public PositionData position;
}

[Serializable]
public class WallData
{
    public int id;
    public PositionData cell_a;
    public PositionData cell_b;
    public int damage;
    public bool is_destroyed;
}

[Serializable]
public class DoorData
{
    public int id;
    public PositionData cell_a;
    public PositionData cell_b;
    public bool is_open;
    public bool is_destroyed;
}


[Serializable]
public class SimulationState
{
    // Tablero
    public int width;
    public int height;

    // Turnos
    public int turn;
    public string phase;
    public int active_doctor_id;

    // Estado general
    public bool running;
    public bool game_over;
    public string game_result;

    // Contadores
    public int house_damage;
    public int patients_rescued;
    public int patients_killed;

    // Elementos del tablero
    public WallData[] walls;
    public DoorData[] doors;

    // Entidades
    public EntityData[] rat_swarms;
    public EntityData[] rat_kings;
    public EntityData[] pois;
    public EntityData[] patients;

    // Doctores
    public DoctorData[] doctors;
}