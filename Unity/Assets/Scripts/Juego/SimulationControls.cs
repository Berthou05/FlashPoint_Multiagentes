using UnityEngine;

public class SimulationControls : MonoBehaviour
{
    // Aquí conectamos el script que se comunica con Python
    public SimulationConnection connection;

    // Reinicia la simulación desde el principio
    public void Reset()
    {
        StartCoroutine(connection.ResetSimulation());
    }

    // Hace que juegue el doctor que tiene el turno
    public void StepDoctor()
    {
        StartCoroutine(connection.StepDoctor());
    }

    // Hace que avance la parte del entorno como las ratas, Rat Kings y demás eventos
    public void StepEnvironment()
    {
        StartCoroutine(connection.StepEnvironment());
    }
}
