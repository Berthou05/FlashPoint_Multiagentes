using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class SimulationConnection : MonoBehaviour
{
    // Dirección donde está corriendo el servidor de Python/Mesa.
    // Si después usan otro puerto, solo cambienlo aquí
    public string baseUrl = "http://127.0.0.1:8585";

    // Aquí guardamos la última respuesta completa que llegó de Python.
    // Incluye tanto los eventos como el estado final.
    public SimulationResponse currentResponse;
   // Referencia al script que dibuja el estado en el tablero
    public SimulationRenderer simRenderer; 

    // Referencias nuevas para la UI
    public HUDController hudController;
    public ActiveDoctorCardController activeDoctorCard;
    [HideInInspector] public CameraTurnFocus cameraTurnFocus;

    public SimulationManager simulationManager;

    void Start()
    {
        ConfigureCameraFocus();

        // Cuando inicia la escena corremos la simulación
        StartCoroutine(ResetAndStartSimulation());
            Debug.Log("Esto se vio 1.");

    }

    // Agrega el controlador a la cámara principal si todavía no está presente.
    // Así no es necesario modificar la escena mientras se está trabajando en ella.
    private void ConfigureCameraFocus()
    {
        Camera sceneCamera = Camera.main;

        // La escena actual no usa la etiqueta MainCamera, así que tomamos
        // la primera cámara disponible como respaldo.
        if (sceneCamera == null)
        {
            sceneCamera = FindAnyObjectByType<Camera>();
        }

        if (sceneCamera == null)
        {
            Debug.LogWarning("No se encontró una cámara en la escena.");
            return;
        }

        CameraTurnFocus cameraFocus =
            sceneCamera.GetComponent<CameraTurnFocus>();

        if (cameraFocus == null)
        {
            cameraFocus = sceneCamera.gameObject.AddComponent<CameraTurnFocus>();
        }

        cameraFocus.connection = this;
        cameraTurnFocus = cameraFocus;
    }

    private IEnumerator ResetAndStartSimulation()
    {
        yield return StartCoroutine(ResetSimulation());
        simulationManager.OnClickStartAutoPlay();
    }

    public IEnumerator GetState()
    {
        return SendRequest("/state", UnityWebRequest.kHttpVerbGET);
    }


    // Estas tres funciones pueden conectarse directamente a botones de Unity.
    // El servidor decide todas las acciones; Unity solo solicita una fase.
    public IEnumerator ResetSimulation(string strategy = "intelligent", int numAgents = 6, int seed = 25)
    {
        ResetRequest reset = new ResetRequest();
        reset.strategy = strategy;
        reset.num_agents = numAgents;
        reset.seed = seed;

        return SendRequest(
            "/reset",
            UnityWebRequest.kHttpVerbPOST,
            JsonUtility.ToJson(reset)
        );
    }


    public IEnumerator StepDoctor()
    {
        return SendRequest("/step_doctor", UnityWebRequest.kHttpVerbPOST, "{}");
    }


    public IEnumerator StepEnvironment()
    {
        return SendRequest("/step_environment", UnityWebRequest.kHttpVerbPOST, "{}");
    }

    public IEnumerator StepCompleteTurn()
    {
        return SendRequest("/step_complete_turn", UnityWebRequest.kHttpVerbPOST, "{}");
    }

  // Wrappers para poder conectar estas acciones directamente a botones de UI
    public void OnClickStepDoctor()
    {
        StartCoroutine(StepDoctor());
    }

    public void OnClickStepEnvironment()
    {
        StartCoroutine(StepEnvironment());
    }

    public void OnClickStepCompleteTurn()
    {
        StartCoroutine(StepCompleteTurn());
    }

    public void OnClickReset()
    {
        StartCoroutine(ResetSimulation());
    }

    private IEnumerator SendRequest(string endpoint, string method, string body = null)
    {
        string url = baseUrl + endpoint;

        UnityWebRequest request = new UnityWebRequest(url, method);
        request.downloadHandler = new DownloadHandlerBuffer();

        if (body != null)
        {
            request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            request.SetRequestHeader("Content-Type", "application/json");
        }

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
                if (simRenderer != null)
                {
                    yield return StartCoroutine(
                        simRenderer.RenderResponse(currentResponse, activeDoctorCard)
                    );
                }

                if (hudController != null)
                {
                    hudController.UpdateHUD();
                }

                if (activeDoctorCard != null)
                {
                    activeDoctorCard.UpdateActiveCard();
                }

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


[System.Serializable]
public class ResetRequest
{
    public string strategy;
    public int num_agents;
    public int seed;
}
