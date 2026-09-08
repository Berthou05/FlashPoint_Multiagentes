using UnityEngine;

public class MostrarPosicionesMuros : MonoBehaviour
{
    void Start()
    {
        Wall[] walls = GetComponentsInChildren<Wall>(true);

        for (int i = 0; i < walls.Length; i++)
        {
            Debug.Log(
            walls[i].transform.parent.name + " > " +
            walls[i].gameObject.name +
            " | X = " + walls[i].transform.position.x +
            " | Z = " + walls[i].transform.position.z
        );
        }
    }
}
