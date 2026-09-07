using UnityEngine;

public class SimulationRenderer : MonoBehaviour
{
    // Estos son los objetos que Unity va a crear en el tablero
    public GameObject doctor;
    public GameObject ratSwarm;
    public GameObject ratKing;
    public GameObject poi;
    public GameObject patient;

    // Este script es el que convierte las coordenadas x,y de Mesa
    // a una posición dentro de Unity
    public BoardPositionConverter positionConverter;

    // Aquí se toma la información que llegó de Python
    public SimulationConnection connection;

    // Esta función toma el estado actual y muestra todo en el tablero
    public void RenderState()
    {
        // Se revisa que sí haya llegado una respuesta
        if (connection.currentResponse == null)
        {
            Debug.LogError("No hay respuesta de la simulación.");
            return;
        }

        // También revisamos que la respuesta tenga un estado
        if (connection.currentResponse.state == null)
        {
            Debug.LogError("No hay estado para mostrar.");
            return;
        }

        // Guardamos el estado en una variable más corta
        // para no tener que escribir connection.currentResponse.state todo el tiempo
        SimulationState state = connection.currentResponse.state;

        // Mostramos cada tipo de objeto que exista
        RenderDoctors(state.doctors);
        RenderRatSwarms(state.rat_swarms);
        RenderRatKings(state.rat_kings);
        RenderPois(state.pois);
        RenderPatients(state.patients);
    }

    void RenderDoctors(DoctorData[] doctors)
    {
        // Si no llegaron doctores, simplemente no hacemos nada
        if (doctors == null)
        {
            return;
        }

        // Recorremos todos los doctores que mandó Python
        for (int i = 0; i < doctors.Length; i++)
        {
            // Convertimos su x,y a una posición de Unity
            Vector3 posicionUnity =
                positionConverter.ConvertToUnityPosition(
                    doctors[i].x,
                    doctors[i].y
                );

            // Creamos el doctor en esa posición
            Instantiate(
                doctor,
                posicionUnity,
                Quaternion.identity
            );
        }
    }

    // Eso se repite para todos los objetos.

    void RenderRatSwarms(EntityData[] rats)
    {
        if (rats == null)
        {
            return;
        }

        for (int i = 0; i < rats.Length; i++)
        {
            Vector3 posicionUnity =
                positionConverter.ConvertToUnityPosition(
                    rats[i].x,
                    rats[i].y
                );

            Instantiate(
                ratSwarm,
                posicionUnity,
                Quaternion.identity
            );
        }
    }

    void RenderRatKings(EntityData[] kings)
    {
        if (kings == null)
        {
            return;
        }

        for (int i = 0; i < kings.Length; i++)
        {
            Vector3 posicionUnity =
                positionConverter.ConvertToUnityPosition(
                    kings[i].x,
                    kings[i].y
                );

            Instantiate(
                ratKing,
                posicionUnity,
                Quaternion.identity
            );
        }
    }

    void RenderPois(EntityData[] pois)
    {
        if (pois == null)
        {
            return;
        }

        for (int i = 0; i < pois.Length; i++)
        {
            Vector3 posicionUnity =
                positionConverter.ConvertToUnityPosition(
                    pois[i].x,
                    pois[i].y
                );

            Instantiate(
                poi,
                posicionUnity,
                Quaternion.identity
            );
        }
    }

    void RenderPatients(EntityData[] patients)
    {
        if (patients == null)
        {
            return;
        }

        for (int i = 0; i < patients.Length; i++)
        {
            Vector3 posicionUnity =
                positionConverter.ConvertToUnityPosition(
                    patients[i].x,
                    patients[i].y
                );

            Instantiate(
                patient,
                posicionUnity,
                Quaternion.identity
            );
        }
    }
}