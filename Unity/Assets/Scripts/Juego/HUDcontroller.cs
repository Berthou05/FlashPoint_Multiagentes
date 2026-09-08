using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class HUDController : MonoBehaviour
{
    public SimulationConnection connection;

    [Header("Global Stats")]
    public TMP_Text savedText;
    public TMP_Text killedText;
    public TMP_Text damageText;
    public TMP_Text turnText;

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
        savedText.text = state.patients_rescued + "/7";
        killedText.text = state.patients_killed + "/4";
        damageText.text = state.house_damage + "/24";
        turnText.text = state.turn.ToString();
    }

    private void UpdateDoctor(SimulationState state)
    {
        if (state.doctors == null || state.doctors.Length == 0)
        {
            return;
        }

        DoctorState activeDoctor = null;

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

        doctorNameText.text = "Doctor Alaric";
        doctorIdText.text = "ID # " + activeDoctor.id;

        UpdateActionPoints(activeDoctor.action_points);
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