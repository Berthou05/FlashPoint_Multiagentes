// DoctorCirclesController.cs — crea/borra los círculos de los doctores SIN turno
using System.Collections.Generic;
using UnityEngine;

public class DoctorCirclesController : MonoBehaviour
{
    public SimulationConnection connection;
    public GameObject doctorCirclePrefab;
    public Transform circlesContainer; // con Horizontal Layout Group, spacing negativo

    private Dictionary<int, GameObject> circles = new Dictionary<int, GameObject>();

    public void UpdateDoctorCircles()
    {
        if (connection.currentResponse == null || connection.currentResponse.state == null)
        {
            return;
        }

        SimulationState state = connection.currentResponse.state;
        DoctorData[] doctores = state.doctors;
        List<int> idsQueDebenTenerCirculo = new List<int>();

        if (doctores != null)
        {
            for (int i = 0; i < doctores.Length; i++)
            {
                int id = doctores[i].id;
                if (id == state.active_doctor_id) continue; // el activo no lleva círculo

                idsQueDebenTenerCirculo.Add(id);

                if (!circles.ContainsKey(id))
                {
                    GameObject nuevoCirculo = Instantiate(doctorCirclePrefab, circlesContainer);
                    circles.Add(id, nuevoCirculo);
                    nuevoCirculo.GetComponent<DoctorCircleView>()?.SetData(id);
                }
            }
        }

        List<int> borrar = new List<int>();
        foreach (int id in circles.Keys)
        {
            if (!idsQueDebenTenerCirculo.Contains(id)) borrar.Add(id);
        }

        for (int i = 0; i < borrar.Count; i++)
        {
            Destroy(circles[borrar[i]]);
            circles.Remove(borrar[i]);
        }
    }
}
