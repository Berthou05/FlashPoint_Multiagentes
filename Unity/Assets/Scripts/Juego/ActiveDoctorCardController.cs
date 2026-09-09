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
                    idText.text = "ID # " + state.doctors[i].id;
                }

                UpdateActionPoints(state.doctors[i].action_points);

                return;
            }
        }
    }

    // Actualiza la card mientras Unity reproduce los eventos de un turno.
    public void UpdateFromEvent(SimulationEvent simulationEvent)
    {
        if (simulationEvent == null)
        {
            return;
        }

        if (simulationEvent.type == "doctor_turn_started")
        {
            if (idText != null)
            {
                idText.text = "ID # " + simulationEvent.id;
            }

            UpdateActionPoints(simulationEvent.action_points);
        }
        else if (simulationEvent.type == "doctor_action_completed")
        {
            if (idText != null)
            {
                idText.text = "ID # " + simulationEvent.doctor_id;
            }

            UpdateActionPoints(simulationEvent.action_points_after);
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
            actionPointImages[i].gameObject.SetActive(i < currentAP);
        }
    }
}
