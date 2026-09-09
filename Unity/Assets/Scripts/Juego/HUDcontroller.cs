using UnityEngine;
using UnityEngine.UI;
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

    [Header("Doctor Info")]
    public TMP_Text doctorNameText;
    public TMP_Text doctorIdText;

    [Header("Action Points")]
    public Image[] actionPointImages;
    public Sprite filledAPSprite;
    public Sprite emptyAPSprite;

    public void UpdateHUD()
    {
        if (connection.currentResponse == null || connection.currentResponse.state == null)
        {
            return;
        }

        SimulationState state = connection.currentResponse.state;

        UpdateStats(state);
        UpdateDoctor(state);
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

    private void UpdateDoctor(SimulationState state)
    {
        if (state.doctors == null || state.doctors.Length == 0)
        {
            return;
        }

        DoctorData activeDoctor = null;

        for (int i = 0; i < state.doctors.Length; i++)
        {
            if (state.doctors[i].id == state.active_doctor_id)
            {
                activeDoctor = state.doctors[i];
                break;
            }
        }

        if (activeDoctor == null)
        {
            return;
        }

        if (doctorNameText != null)
        {
            doctorNameText.text = "Doctor Alaric";
        }

        if (doctorIdText != null)
        {
            doctorIdText.text = "ID # " + activeDoctor.id;
        }

        if (actionPointImages != null)
        {
            UpdateActionPoints(activeDoctor.action_points);
        }
    }

    private void UpdateActionPoints(int currentAP)
    {
        for (int i = 0; i < actionPointImages.Length; i++)
        {
            if (i < currentAP)
            {
                actionPointImages[i].sprite = filledAPSprite;
            }
            else
            {
                actionPointImages[i].sprite = emptyAPSprite;
            }
        }
    }
}
