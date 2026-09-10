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

    [Header("Pantallas de fin")]
    public GameObject victoryPanel;
    public GameObject defeatPanel;
    public float endPanelDelay = 3f;

    public bool isPlaying { get; private set; } = false;

    private Coroutine loopCoroutine;
    private Coroutine endPanelCoroutine;

    private void Awake()
    {
        HideEndPanels();
    }

    // Conecta esto a un botón de "Play"/"Iniciar automático"
    public void OnClickStartAutoPlay()
    {
        if (isPlaying) return;

        if (endPanelCoroutine != null)
        {
            StopCoroutine(endPanelCoroutine);
            endPanelCoroutine = null;
        }

        HideEndPanels();
        isPlaying = true;
        loopCoroutine = StartCoroutine(AutoPlayLoop());
    }

    // SimulationConnection llama este método al recibir un estado final.
    public void HandleGameStatus(string gameStatus)
    {
        if (gameStatus != "victory" && gameStatus != "defeat")
        {
            return;
        }

        if (endPanelCoroutine != null)
        {
            return;
        }

        isPlaying = false;
        endPanelCoroutine = StartCoroutine(
            ShowEndPanelAfterDelay(gameStatus)
        );
    }

    private IEnumerator ShowEndPanelAfterDelay(string gameStatus)
    {
        yield return new WaitForSeconds(endPanelDelay);
        ShowEndPanel(gameStatus);
        endPanelCoroutine = null;
    }

    public void ShowEndPanel(string gameStatus)
    {
        bool isVictory = gameStatus == "victory";

        if (victoryPanel != null)
        {
            victoryPanel.SetActive(isVictory);
        }

        if (defeatPanel != null)
        {
            defeatPanel.SetActive(!isVictory);
        }
    }

    private void HideEndPanels()
    {
        if (victoryPanel != null)
        {
            victoryPanel.SetActive(false);
        }

        if (defeatPanel != null)
        {
            defeatPanel.SetActive(false);
        }
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
