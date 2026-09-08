using System.Collections;
using UnityEngine;

public class HourglassToggleButton : MonoBehaviour
{
    // El loop que este botón controla
    public SimulationManager simulationManager;

    // El objeto que tiene la imagen del reloj de arena (puede ser este mismo GameObject)
    public RectTransform hourglassTransform;

    // Cuánto tarda en girar, en segundos
    public float rotationDuration = 0.25f;

    // Ángulos: vertical = reloj "de pie" (play), horizontal = acostado (pausa)
    private const float AnguloVertical = 0f;
    private const float AnguloHorizontal = 90f;

    private Coroutine rotacionEnCurso;

    // Conecta este método al OnClick() del botón
    public void OnClickToggle()
    {
        if (simulationManager.isPlaying)
        {
            simulationManager.OnClickStopAutoPlay();
            GirarHacia(AnguloHorizontal);
        }
        else
        {
            simulationManager.OnClickStartAutoPlay();
            GirarHacia(AnguloVertical);
        }
    }

    private void GirarHacia(float anguloDestino)
    {
        if (rotacionEnCurso != null)
        {
            StopCoroutine(rotacionEnCurso);
        }

        rotacionEnCurso = StartCoroutine(RotarSuave(anguloDestino));
    }

    private IEnumerator RotarSuave(float anguloDestino)
    {
        float anguloInicial = hourglassTransform.localEulerAngles.z;
        float elapsed = 0f;

        while (elapsed < rotationDuration)
        {
            elapsed += Time.deltaTime;
            float anguloActual = Mathf.LerpAngle(
                anguloInicial,
                anguloDestino,
                elapsed / rotationDuration
            );

            hourglassTransform.localEulerAngles = new Vector3(0f, 0f, anguloActual);
            yield return null;
        }

        hourglassTransform.localEulerAngles = new Vector3(0f, 0f, anguloDestino);
        rotacionEnCurso = null;
    }
}