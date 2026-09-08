using System.Collections;
using UnityEngine;

public class SimulationManager : MonoBehaviour
{
    public SimulationConnection connection;

    // Pausa entre cada paso (doctor o ambiente), en segundos.
    // No incluye el tiempo que tarda la animación de movimiento del doctor,
    // eso ya lo maneja SimulationRenderer.RenderResponse antes de que este
    // script pida el siguiente paso.
    public float delayBetweenSteps = 1f;

    public bool isPlaying { get; private set; } = false;

    private Coroutine loopCoroutine;

    // Conecta esto a un botón de "Play"/"Iniciar automático"
    public void OnClickStartAutoPlay()
    {
        if (isPlaying) return;

        isPlaying = true;
        loopCoroutine = StartCoroutine(AutoPlayLoop());
    }

    // Conecta esto a un botón de "Pausa"
    public void OnClickStopAutoPlay()
    {
        isPlaying = false;

        if (loopCoroutine != null)
        {
            StopCoroutine(loopCoroutine);
            loopCoroutine = null;
        }
    }

    private IEnumerator AutoPlayLoop()
    {
        while (isPlaying)
        {
            SimulationState state = connection.currentResponse != null
                ? connection.currentResponse.state
                : null;

            if (state == null)
            {
                yield return StartCoroutine(connection.GetState());
                continue;
            }

            if (state.phase == "finished" || state.game_status != "running")
            {
                isPlaying = false;
                yield break;
            }

            if (state.phase == "doctor")
            {
                yield return StartCoroutine(connection.StepDoctor());
            }
            else if (state.phase == "environment")
            {
                yield return StartCoroutine(connection.StepEnvironment());
            }

            yield return new WaitForSeconds(delayBetweenSteps);
        }
    }
}