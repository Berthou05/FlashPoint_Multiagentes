using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class SimulationConnection : MonoBehaviour
{
    // Esta es la dirección del servidor de Python/Mesa
    public string baseUrl = "http://127.0.0.1:5000";

    // Se guarda el último estado que se haya recibido de la simulación
    public SimulationState currentState;

    void Start()
    {
        StartCoroutine(GetState());
    }

    // Solicita el estado actual a Mesa
    public IEnumerator GetState()
    {
        string url = baseUrl + "/state";

        UnityWebRequest request = UnityWebRequest.Get(url);

        // Espera la respuesta sin detener Unity
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            string json = request.downloadHandler.text;

            // Aquí se convierte el JSON recibido a SimulationState para que encaje
            currentState = JsonUtility.FromJson<SimulationState>(json);

            if (currentState != null)
            {
                Debug.Log("Conectado con Mesa");
                Debug.Log("Tablero: " + currentState.width + " x " + currentState.height);

                if (currentState.doctors != null)
                {
                    Debug.Log("Doctores: " + currentState.doctors.Length);
                }
            }
            else
            {
                Debug.LogError("No se pudo convertir el JSON recibido.");
            }
        }
        else
        {
            Debug.LogError("Error al conectar con Mesa: " + request.error);
        }

        request.Dispose();
    }
}