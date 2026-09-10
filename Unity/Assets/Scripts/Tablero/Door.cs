using UnityEngine;

public class Door : MonoBehaviour
{
    public int ax;
    public int ay;
    public int bx;
    public int by;

    public bool isOpen;
    public bool isDestroyed;

    public Transform hinge;
    public MeshRenderer doorRenderer;

    public Material normal;
    public Material destroyed;

    private Quaternion closedRotation;
    private BoxCollider boxCollider;

    void Awake()
    {
        boxCollider = GetComponent<BoxCollider>();
        closedRotation = hinge.localRotation;

        AssignCoordinates();
        ApplyDoorVisual();
    }

    void OnValidate()
    {
        if (hinge == null)
        {
            return;
        }

        if (!Application.isPlaying)
        {
            closedRotation = Quaternion.identity;
        }

        ApplyDoorVisual();
    }

    void AssignCoordinates()
    {
        float x = transform.position.x;
        float z = transform.position.z;

        if (transform.lossyScale.x > transform.lossyScale.z)
        {
            int cellX = Mathf.RoundToInt(x / 4f) + 1;
            int cellY = Mathf.RoundToInt((2f - z) / 4f);

            ax = cellX;
            ay = cellY;

            bx = cellX;
            by = cellY + 1;
        }
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

    public void UpdateDoor(bool open, bool destroyedState)
    {
        isOpen = open;
        isDestroyed = destroyedState;

        ApplyDoorVisual();
    }

    void ApplyDoorVisual()
    {
        if (hinge == null)
        {
            return;
        }

        if (isDestroyed)
        {
            if (doorRenderer != null && destroyed != null)
            {
                doorRenderer.material = destroyed;
            }

            hinge.localRotation = closedRotation;

            if (boxCollider != null)
            {
                boxCollider.enabled = false;
            }
        }
        else
        {
            if (doorRenderer != null && normal != null)
            {
                doorRenderer.material = normal;
            }

            if (isOpen)
            {
                hinge.localRotation = closedRotation * Quaternion.Euler(0f, 90f, 0f);

                if (boxCollider != null)
                {
                    boxCollider.enabled = false;
                }
            }
            else
            {
                hinge.localRotation = closedRotation;

                if (boxCollider != null)
                {
                    boxCollider.enabled = true;
                }
            }
        }
    }
}