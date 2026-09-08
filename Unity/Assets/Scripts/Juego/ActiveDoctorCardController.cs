// ActiveDoctorCardController.cs — la única card grande, siempre visible
using UnityEngine;
using TMPro;

public class ActiveDoctorCardController : MonoBehaviour
{
    public SimulationConnection connection;
    public TMP_Text idText;
    public TMP_Text apText;

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
                idText.text = "Doctor " + state.doctors[i].id;
                apText.text = "AP: " + state.doctors[i].action_points;
                return;
            }
        }
    }
}