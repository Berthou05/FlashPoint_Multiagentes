// ActiveDoctorCardController.cs — la única card grande, siempre visible
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ActiveDoctorCardController : MonoBehaviour
{
    public SimulationConnection connection;
    public TMP_Text idText;
    public Image[] actionPointImages;

    public void UpdateActiveCard()
    {
        if (connection.currentResponse == null || connection.currentResponse.state == null)
        {
            return;
        }

        SimulationState state = connection.currentResponse.state;
        if (state.doctors == null) return;

        for (int i = 0; i < state.doctors.Length; i++)
        {
            if (state.doctors[i].id == state.active_doctor_id)
            {
                if (idText != null)
                {
                    idText.text = "Doctor " + state.doctors[i].id;
                }

                UpdateActionPoints(state.doctors[i].action_points);

                return;
            }
        }
    }

    private void UpdateActionPoints(int currentAP)
    {
        if (actionPointImages == null)
        {
            return;
        }

        for (int i = 0; i < actionPointImages.Length; i++)
        {
            if (actionPointImages[i] == null)
            {
                continue;
            }

            actionPointImages[i].gameObject.SetActive(true);
            actionPointImages[i].color = i < currentAP
                ? Color.white
                : new Color(1f, 1f, 1f, 0.25f);
        }
    }
}
