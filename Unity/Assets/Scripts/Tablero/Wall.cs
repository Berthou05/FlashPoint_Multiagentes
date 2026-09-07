using UnityEngine;

public class Wall : MonoBehaviour
{
    public int ax;
    public int ay;
    public int bx;
    public int by;

    public void UpdateWall(int damage, bool destroyed)
    {
        Debug.Log(
            "Muro " + ax + "," + ay +
            " - " + bx + "," + by +
            " | Daño: " + damage +
            " | Destruido: " + destroyed
        );

        gameObject.SetActive(!destroyed);
    }
}
