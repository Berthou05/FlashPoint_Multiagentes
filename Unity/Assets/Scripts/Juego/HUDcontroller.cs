using UnityEngine;
using TMPro; // si usas Text normal en vez de TextMeshPro, cambia esto por UnityEngine.UI

public class HUDController : MonoBehaviour
{
    // Referencia a la conexión para leer el estado más reciente
    public SimulationConnection connection;

    // Arrastra aquí los textos de tu Canvas (uno por dato)
    public TMP_Text turnoText;
    public TMP_Text victimasRescatadasText;
    public TMP_Text victimasMuertasText;
    public TMP_Text danoCasaText;

    // Llama esto después de cada RenderState(), o cada vez que quieras refrescar el HUD
    public void UpdateHUD()
    {
        if (connection.currentResponse == null || connection.currentResponse.state == null)
        {
            return;
        }

        SimulationState state = connection.currentResponse.state;

        turnoText.text = "Turno: " + state.turn;
        victimasRescatadasText.text = "Rescatados: " + state.patients_rescued;
        victimasMuertasText.text = "Muertos: " + state.patients_killed;
        danoCasaText.text = "Daño casa: " + state.house_damage;
    }
}