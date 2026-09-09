using UnityEngine;
using TMPro;

public class HUDController : MonoBehaviour
{
    public SimulationConnection connection;

    [Header("Global Stats")]
    // Estos nombres coinciden con las referencias guardadas en la escena.
    public TMP_Text victimasRescatadasText;
    public TMP_Text victimasMuertasText;
    public TMP_Text danoCasaText;
    public TMP_Text turnoText;

    public void UpdateHUD()
    {
        if (connection.currentResponse == null || connection.currentResponse.state == null)
        {
            return;
        }

        SimulationState state = connection.currentResponse.state;

        UpdateStats(state);
    }

    private void UpdateStats(SimulationState state)
    {
        if (victimasRescatadasText != null)
        {
            victimasRescatadasText.text = state.patients_rescued + "/7";
        }

        if (victimasMuertasText != null)
        {
            victimasMuertasText.text = state.patients_killed + "/4";
        }

        if (danoCasaText != null)
        {
            danoCasaText.text = state.house_damage + "/24";
        }

        if (turnoText != null)
        {
            turnoText.text = state.turn.ToString();
        }
    }

}
