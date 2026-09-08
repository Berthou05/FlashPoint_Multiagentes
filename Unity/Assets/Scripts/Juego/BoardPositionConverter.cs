using UnityEngine;

public class BoardPositionConverter : MonoBehaviour
{
    public float cellSize = 4f;

    public Vector3 ConvertToUnityPosition(int x, int y)
    {
        float posicionX = (x - 1) * cellSize;
        float posicionZ = -(y - 1) * cellSize;

        return new Vector3(posicionX, 0f, posicionZ);
    }
}
