using System.Collections.Generic;
using UnityEngine;

public class SimulationRenderer : MonoBehaviour
{
    // Prefabs que se van a mostrar en el tablero
    public GameObject doctor;
    public GameObject ratSwarm;
    public GameObject ratKing;
    public GameObject poi;
    public GameObject patient;

    // Convierte las coordenadas de Mesa a Unity
    public BoardPositionConverter positionConverter;

    // Conexión con Python
    public SimulationConnection connection;

    // Aquí guardamos los objetos que ya existen en Unity.
    // El número es el ID que manda Mesa.
    private Dictionary<int, GameObject> doctors = new Dictionary<int, GameObject>();
    private Dictionary<int, GameObject> ratSwarms = new Dictionary<int, GameObject>();
    private Dictionary<int, GameObject> ratKings = new Dictionary<int, GameObject>();
    private Dictionary<int, GameObject> pois = new Dictionary<int, GameObject>();
    private Dictionary<int, GameObject> patients = new Dictionary<int, GameObject>();


    // Actualiza Unity para que coincida con el estado de Mesa
    public void RenderState()
    {
        if (connection.currentResponse == null)
        {
            Debug.LogError("No hay respuesta de la simulación.");
            return;
        }

        if (connection.currentResponse.state == null)
        {
            Debug.LogError("No hay estado para mostrar.");
            return;
        }

        SimulationState state = connection.currentResponse.state;

        RenderDoctors(state.doctors);
        RenderRatSwarms(state.rat_swarms);
        RenderRatKings(state.rat_kings);
        RenderPois(state.pois);
        RenderPatients(state.patients);
        RenderWalls(state.walls);
    }


    void RenderDoctors(DoctorData[] datos)
    {
        List<int> idsActuales = new List<int>();

        if (datos != null)
        {
            for (int i = 0; i < datos.Length; i++)
            {
                int id = datos[i].id;
                idsActuales.Add(id);

                Vector3 posicion =
                    positionConverter.ConvertToUnityPosition(
                        datos[i].x,
                        datos[i].y
                    );

                // Si todavía no existe, lo creamos
                if (!doctors.ContainsKey(id))
                {
                    GameObject nuevoDoctor =
                        Instantiate(
                            doctor,
                            posicion,
                            Quaternion.identity
                        );

                    nuevoDoctor.name = "Doctor_" + id;

                    doctors.Add(id, nuevoDoctor);
                }
                else
                {
                    // Si ya existe, solo actualizamos su posición
                    doctors[id].transform.position = posicion;
                }
            }
        }

        RemoveMissingDoctors(idsActuales);
    }


    void RenderRatSwarms(EntityData[] datos)
    {
        List<int> idsActuales = new List<int>();

        if (datos != null)
        {
            for (int i = 0; i < datos.Length; i++)
            {
                int id = datos[i].id;
                idsActuales.Add(id);

                Vector3 posicion =
                    positionConverter.ConvertToUnityPosition(
                        datos[i].x,
                        datos[i].y
                    );

                if (!ratSwarms.ContainsKey(id))
                {
                    GameObject nuevo =
                        Instantiate(
                            ratSwarm,
                            posicion,
                            Quaternion.identity
                        );

                    nuevo.name = "RatSwarm_" + id;

                    ratSwarms.Add(id, nuevo);
                }
                else
                {
                    ratSwarms[id].transform.position = posicion;
                }
            }
        }

        RemoveMissingRatSwarms(idsActuales);
    }


    void RenderRatKings(EntityData[] datos)
    {
        List<int> idsActuales = new List<int>();

        if (datos != null)
        {
            for (int i = 0; i < datos.Length; i++)
            {
                int id = datos[i].id;
                idsActuales.Add(id);

                Vector3 posicion =
                    positionConverter.ConvertToUnityPosition(
                        datos[i].x,
                        datos[i].y
                    );

                if (!ratKings.ContainsKey(id))
                {
                    GameObject nuevo =
                        Instantiate(
                            ratKing,
                            posicion,
                            Quaternion.identity
                        );

                    nuevo.name = "RatKing_" + id;

                    ratKings.Add(id, nuevo);
                }
                else
                {
                    ratKings[id].transform.position = posicion;
                }
            }
        }

        RemoveMissingRatKings(idsActuales);
    }


    void RenderPois(EntityData[] datos)
    {
        List<int> idsActuales = new List<int>();

        if (datos != null)
        {
            for (int i = 0; i < datos.Length; i++)
            {
                int id = datos[i].id;
                idsActuales.Add(id);

                Vector3 posicion =
                    positionConverter.ConvertToUnityPosition(
                        datos[i].x,
                        datos[i].y
                    );

                if (!pois.ContainsKey(id))
                {
                    GameObject nuevo =
                        Instantiate(
                            poi,
                            posicion,
                            Quaternion.identity
                        );

                    nuevo.name = "POI_" + id;

                    pois.Add(id, nuevo);
                }
                else
                {
                    pois[id].transform.position = posicion;
                }
            }
        }

        RemoveMissingPois(idsActuales);
    }


    void RenderPatients(EntityData[] datos)
    {
        List<int> idsActuales = new List<int>();

        if (datos != null)
        {
            for (int i = 0; i < datos.Length; i++)
            {
                int id = datos[i].id;
                idsActuales.Add(id);

                Vector3 posicion =
                    positionConverter.ConvertToUnityPosition(
                        datos[i].x,
                        datos[i].y
                    );

                if (!patients.ContainsKey(id))
                {
                    GameObject nuevo =
                        Instantiate(
                            patient,
                            posicion,
                            Quaternion.identity
                        );

                    nuevo.name = "Patient_" + id;

                    patients.Add(id, nuevo);
                }
                else
                {
                    patients[id].transform.position = posicion;
                }
            }
        }

        RemoveMissingPatients(idsActuales);
    }

    void RenderWalls(WallData[] datos)
    {
        if (datos == null)
        {
            return;
        }

        GameObject wallsObject = GameObject.Find("Walls");

        if (wallsObject == null)
        {
            Debug.LogError("No se encontró el objeto Walls.");
            return;
        }

        Wall[] walls = wallsObject.GetComponentsInChildren<Wall>(true);

        for (int i = 0; i < datos.Length; i++)
        {
            for (int j = 0; j < walls.Length; j++)
            {
                bool mismasCoordenadas =
                    (walls[j].ax == datos[i].ax &&
                    walls[j].ay == datos[i].ay &&
                    walls[j].bx == datos[i].bx &&
                    walls[j].by == datos[i].by)
                    ||
                    (walls[j].ax == datos[i].bx &&
                    walls[j].ay == datos[i].by &&
                    walls[j].bx == datos[i].ax &&
                    walls[j].by == datos[i].ay);

                if (mismasCoordenadas)
                {
                    walls[j].UpdateWall(
                        datos[i].damage,
                        datos[i].destroyed
                    );
                }
            }
        }
    }


    void RemoveMissingDoctors(List<int> idsActuales)
    {
        List<int> borrar = new List<int>();

        foreach (int id in doctors.Keys)
        {
            if (!idsActuales.Contains(id))
            {
                borrar.Add(id);
            }
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(doctors[borrar[i]]);
            doctors.Remove(borrar[i]);
        }
    }


    void RemoveMissingRatSwarms(List<int> idsActuales)
    {
        List<int> borrar = new List<int>();

        foreach (int id in ratSwarms.Keys)
        {
            if (!idsActuales.Contains(id))
            {
                borrar.Add(id);
            }
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(ratSwarms[borrar[i]]);
            ratSwarms.Remove(borrar[i]);
        }
    }


    void RemoveMissingRatKings(List<int> idsActuales)
    {
        List<int> borrar = new List<int>();

        foreach (int id in ratKings.Keys)
        {
            if (!idsActuales.Contains(id))
            {
                borrar.Add(id);
            }
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(ratKings[borrar[i]]);
            ratKings.Remove(borrar[i]);
        }
    }


    void RemoveMissingPois(List<int> idsActuales)
    {
        List<int> borrar = new List<int>();

        foreach (int id in pois.Keys)
        {
            if (!idsActuales.Contains(id))
            {
                borrar.Add(id);
            }
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(pois[borrar[i]]);
            pois.Remove(borrar[i]);
        }
    }


    void RemoveMissingPatients(List<int> idsActuales)
    {
        List<int> borrar = new List<int>();

        foreach (int id in patients.Keys)
        {
            if (!idsActuales.Contains(id))
            {
                borrar.Add(id);
            }
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(patients[borrar[i]]);
            patients.Remove(borrar[i]);
        }
    }
}