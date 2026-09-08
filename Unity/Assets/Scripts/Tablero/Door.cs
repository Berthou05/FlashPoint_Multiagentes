using UnityEngine;

public class Door : MonoBehaviour
{
    public int ax;
    public int ay;
    public int bx;
    public int by;

    public bool isOpen;
    public bool isDestroyed;

    void Awake()
    {
        AssignCoordinates();
    }

    void AssignCoordinates()
    {
        float x = transform.position.x;
        float z = transform.position.z;

        // Puerta horizontal
        if (transform.lossyScale.x > transform.lossyScale.z)
        {
            int cellX = Mathf.RoundToInt(x / 4f) + 1;
            int cellY = Mathf.RoundToInt((2f - z) / 4f);

            ax = cellX;
            ay = cellY;

            bx = cellX;
            by = cellY + 1;
        }

        // Puerta vertical
        else
        {
            int cellX = Mathf.RoundToInt((x + 2f) / 4f);
            int cellY = Mathf.RoundToInt(1f - z / 4f);

            ax = cellX;
            ay = cellY;

            bx = cellX + 1;
            by = cellY;
        }
    }
}
