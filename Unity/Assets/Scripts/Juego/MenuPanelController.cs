using System.Collections;
using UnityEngine;

public class MenuPanelController : MonoBehaviour
{
    public GameObject menuPanel;
    public RectTransform menuCard;
    public HourglassToggleButton hourglassButton;
    public float slideDuration = 0.35f;

    private Vector2 finalPosition;
    private bool restartHourglass;
    private Coroutine slideCoroutine;

    private void Awake()
    {
        finalPosition = menuCard.anchoredPosition;
        menuPanel.SetActive(false);
    }

    // El mismo botón abre y cierra el menú.
    public void OnClickMenu()
    {
        if (menuPanel.activeSelf)
        {
            CloseMenu();
            return;
        }

        restartHourglass = hourglassButton.simulationManager.isPlaying;
        hourglassButton.Pause();
        menuPanel.SetActive(true);

        // La tarjeta inicia arriba de su posición final y baja hasta ella.
        menuCard.anchoredPosition =
            finalPosition + Vector2.up * menuCard.rect.height;
        slideCoroutine = StartCoroutine(SlideMenuDown());
    }

    private void CloseMenu()
    {
        if (slideCoroutine != null)
        {
            StopCoroutine(slideCoroutine);
            slideCoroutine = null;
        }

        menuPanel.SetActive(false);

        if (restartHourglass)
        {
            hourglassButton.Resume();
        }

        restartHourglass = false;
    }

    private IEnumerator SlideMenuDown()
    {
        Vector2 initialPosition = menuCard.anchoredPosition;
        float elapsed = 0f;

        while (elapsed < slideDuration)
        {
            elapsed += Time.unscaledDeltaTime;
            menuCard.anchoredPosition = Vector2.Lerp(
                initialPosition,
                finalPosition,
                elapsed / slideDuration
            );
            yield return null;
        }

        menuCard.anchoredPosition = finalPosition;
        slideCoroutine = null;
    }
}
