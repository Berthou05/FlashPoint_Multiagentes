// DoctorCircleView.cs — vive en cada círculo individual
using UnityEngine;

public class DoctorCircleView : MonoBehaviour
{
    public void SetData(int id)
    {
        gameObject.name = "DoctorCircle_" + id;
    }
}