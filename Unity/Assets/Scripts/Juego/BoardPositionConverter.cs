using UnityEngine;

public class BoardPositionConverter : MonoBehaviour
{
    // Tamaño de cada casilla del tablero en Unity
    public float cellSize = 4f;

    // Convierte las coordenadas X,Y de Mesa
    // a la posición X,Y,Z de Unity
    public Vector3 ConvertToUnityPosition(int x, int y)
    {
        float posicionX = x * cellSize;
        float posicionZ = -y * cellSize;

        // Y es 0 porque representa la altura en Unity
        return new Vector3(posicionX, 0f, posicionZ);
    }
}
