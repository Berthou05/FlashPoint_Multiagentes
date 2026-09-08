using UnityEngine;

public class Wall : MonoBehaviour
{
    public int ax;
    public int ay;
    public int bx;
    public int by;

    public Material normal;
    public Material damaged;
    public Material destroyed;

    private MeshRenderer meshRenderer;
    private BoxCollider boxCollider;

    void Awake()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        boxCollider = GetComponent<BoxCollider>();

        AssignCoordinates();
    }

    void AssignCoordinates()
    {
        float x = transform.position.x;
        float z = transform.position.z;

        // Muro horizontal
        if (transform.lossyScale.x > transform.lossyScale.z)
        {
            int cellX = Mathf.RoundToInt(x / 4f) + 1;
            int cellY = Mathf.RoundToInt((2f - z) / 4f);

            ax = cellX;
            ay = cellY;

            bx = cellX;
            by = cellY + 1;
        }

        // Muro vertical
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

    public void UpdateWall(int damage, bool isDestroyed)
    {
        if (isDestroyed)
        {
            meshRenderer.material = destroyed;
            boxCollider.enabled = false;
        }
        else if (damage == 1)
        {
            meshRenderer.material = damaged;
            boxCollider.enabled = true;
        }
        else
        {
            meshRenderer.material = normal;
            boxCollider.enabled = true;
        }
    }
}