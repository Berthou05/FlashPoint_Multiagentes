using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class SimulationConnection : MonoBehaviour
{
    // Dirección donde está corriendo el servidor de Python/Mesa.
    // Si después usan otro puerto, solo cambienlo aquí
    public string baseUrl = "http://127.0.0.1:5000";

    // Aquí guardamos la última respuesta completa que llegó de Python.
    // Incluye tanto los eventos como el estado final.
    public SimulationResponse currentResponse;


    void Start()
    {
        // Cuando empieza la escena pedimos el estado actual de la simulación.
        StartCoroutine(GetState());
    }


    public IEnumerator GetState()
    {
        // Forma la dirección url:
    
        string url = baseUrl + "/state";

        // Prepara una petición GET al servidor de Python
        UnityWebRequest request = UnityWebRequest.Get(url);

        // Espera la respuesta sin congelar Unity
        yield return request.SendWebRequest();


        // Si Python respondió correctamente
        if (request.result == UnityWebRequest.Result.Success)
        {
            // Guardamos primero la respuesta como texto
            string json = request.downloadHandler.text;

            // Convertimos ese JSON a las clases que hicimos
            currentResponse = JsonUtility.FromJson<SimulationResponse>(json);


            // Revisamos que realmente haya llegado 
            if (currentResponse != null &&
                currentResponse.state != null)
            {
                Debug.Log("Conectado con Mesa");

                Debug.Log(
                    "API: " + currentResponse.api_version );

                Debug.Log("Versión del estado: " + currentResponse.state_version );

                Debug.Log( "Tablero: " + currentResponse.state.width + " x " + currentResponse.state.height );

                Debug.Log( "Turno: " + currentResponse.state.turn );

                Debug.Log( "Fase: " + currentResponse.state.phase );


                // Solo intentamos contar doctores si realmente llegó la lista
                if (currentResponse.state.doctors != null)
                {
                    Debug.Log(
                        "Doctores: " + currentResponse.state.doctors.Length );
                }


                // Igual con los eventos
                if (currentResponse.events != null)
                {
                    Debug.Log( "Eventos recibidos: " + currentResponse.events.Length );

                    // Aquí solo se muestra cada evento en la console.
                    for (int i = 0; i < currentResponse.events.Length; i++)
                    {
                        Debug.Log( "Evento " + currentResponse.events[i].sequence + ": " + currentResponse.events[i].type
                        );
                    }
                }
            }
            else
            {
                Debug.LogError(
                    "Llegó una respuesta, pero Unity no pudo convertir el JSON."
                );
            }
        }

        // Si no pudimos comunicarnos con Python
        else
        {
            Debug.LogError(
                "Error al conectar con Mesa: " +
                request.error
            );
        }


        // Cerramos la petición cuando ya terminamos de utilizarla
        request.Dispose();
    }
}