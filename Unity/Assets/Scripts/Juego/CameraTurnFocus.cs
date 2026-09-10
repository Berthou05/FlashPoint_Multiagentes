using UnityEngine;

// Enfoca al doctor activo durante su turno y vuelve a la vista general
// cuando empieza la fase de ambiente.
public class CameraTurnFocus : MonoBehaviour
{
    public SimulationConnection connection;

    [Header("Vista del doctor")]
    [Range(0f, 1f)]
    public float followPositionFactor = 0.3f;
    public float maxHorizontalDisplacement = 2.5f;
    public float maxDepthDisplacement = 2f;
    public float doctorFieldOfView = 48f;
    public float doctorOrthographicSize = 8f;

    [Header("Vista de ambiente")]
    [Range(0f, 1f)]
    public float environmentPositionFactor = 0.12f;

    [Header("Transiciones")]
    public float followSmoothTime = 1.2f;
    public float returnSmoothTime = 1f;
    public float rotationSpeed = 2f;
    public float zoomSpeed = 1.2f;

    private Camera sceneCamera;
    private Vector3 originalPosition;
    private Quaternion originalRotation;
    private float originalFieldOfView;
    private float originalOrthographicSize;
    private Vector3 movementVelocity;
    private bool isFollowingDoctor;
    private int activeDoctorId = -1;
    private bool isFocusingEnvironment;
    private Vector3 environmentPosition;

    void Awake()
    {
        sceneCamera = GetComponent<Camera>();

        originalPosition = transform.position;
        originalRotation = transform.rotation;

        if (sceneCamera != null)
        {
            originalFieldOfView = sceneCamera.fieldOfView;
            originalOrthographicSize = sceneCamera.orthographicSize;
        }
    }

    void LateUpdate()
    {
        SimulationState state = GetCurrentState();

        if (isFocusingEnvironment && state != null)
        {
            FocusOnEnvironment(state);
            return;
        }

        if (isFollowingDoctor && state != null)
        {
            GameObject activeDoctor = GameObject.Find(
                "Doctor_" + activeDoctorId
            );

            if (activeDoctor != null)
            {
                FocusOnDoctor(activeDoctor.transform.position, state);
                return;
            }
        }

        RestoreOriginalView();
    }

    private SimulationState GetCurrentState()
    {
        if (connection == null || connection.currentResponse == null)
        {
            return null;
        }

        return connection.currentResponse.state;
    }

    // El renderer llama a este método antes de animar las acciones del doctor.
    public void BeginDoctorTurn(int doctorId)
    {
        activeDoctorId = doctorId;
        isFollowingDoctor = true;
    }

    // El renderer llama a este método al terminar la animación del turno.
    public void EndDoctorTurn()
    {
        isFollowingDoctor = false;
        activeDoctorId = -1;
    }

    // El renderer llama este método cuando una infestación cambia durante
    // la fase de ambiente.
    public void BeginEnvironmentFocus(Vector3 infestationPosition)
    {
        environmentPosition = infestationPosition;
        isFocusingEnvironment = true;
    }

    public void EndEnvironmentFocus()
    {
        isFocusingEnvironment = false;
    }

    private void FocusOnDoctor(Vector3 doctorPosition, SimulationState state)
    {
        Vector3 boardCenter = GetBoardCenter(state);
        Vector3 desiredPosition = CalculateFollowPosition(
            originalPosition,
            boardCenter,
            doctorPosition,
            followPositionFactor,
            maxHorizontalDisplacement,
            maxDepthDisplacement
        );

        // Conservamos el ángulo original de la casa. Solo desplazamos la
        // vista ligeramente hacia el doctor y con límites seguros.
        transform.position = Vector3.SmoothDamp(
            transform.position,
            desiredPosition,
            ref movementVelocity,
            followSmoothTime
        );

        SetZoom(
            doctorFieldOfView,
            doctorOrthographicSize,
            zoomSpeed
        );
    }

    private void FocusOnEnvironment(SimulationState state)
    {
        Vector3 desiredPosition = CalculateFollowPosition(
            originalPosition,
            GetBoardCenter(state),
            environmentPosition,
            environmentPositionFactor,
            maxHorizontalDisplacement,
            maxDepthDisplacement
        );

        transform.position = Vector3.SmoothDamp(
            transform.position,
            desiredPosition,
            ref movementVelocity,
            followSmoothTime
        );

        SetZoom(
            originalFieldOfView,
            originalOrthographicSize,
            zoomSpeed
        );
    }

    // Mantiene la composición de la cámara original y solo la desplaza
    // parcialmente hacia el médico. Así no sale de los límites de la casa.
    public static Vector3 CalculateFollowPosition(
        Vector3 originalPosition,
        Vector3 boardCenter,
        Vector3 doctorPosition,
        float positionFactor,
        float maxHorizontalDisplacement,
        float maxDepthDisplacement
    )
    {
        Vector3 displacement =
            (doctorPosition - boardCenter) * positionFactor;

        displacement.x = Mathf.Clamp(
            displacement.x,
            -maxHorizontalDisplacement,
            maxHorizontalDisplacement
        );
        displacement.z = Mathf.Clamp(
            displacement.z,
            -maxDepthDisplacement,
            maxDepthDisplacement
        );

        return originalPosition + displacement;
    }

    private Vector3 GetBoardCenter(SimulationState state)
    {
        float cellSize = 4f;

        if (connection != null &&
            connection.simRenderer != null &&
            connection.simRenderer.positionConverter != null)
        {
            cellSize = connection.simRenderer.positionConverter.cellSize;
        }

        return new Vector3(
            (state.width - 1) * cellSize / 2f,
            0f,
            -(state.height - 1) * cellSize / 2f
        );
    }

    private void RestoreOriginalView()
    {
        transform.position = Vector3.SmoothDamp(
            transform.position,
            originalPosition,
            ref movementVelocity,
            returnSmoothTime
        );

        transform.rotation = Quaternion.Slerp(
            transform.rotation,
            originalRotation,
            Time.deltaTime * rotationSpeed
        );

        SetZoom(
            originalFieldOfView,
            originalOrthographicSize,
            zoomSpeed
        );
    }

    private void SetZoom(
        float fieldOfView,
        float orthographicSize,
        float speed
    )
    {
        if (sceneCamera == null)
        {
            return;
        }

        if (sceneCamera.orthographic)
        {
            sceneCamera.orthographicSize = Mathf.Lerp(
                sceneCamera.orthographicSize,
                orthographicSize,
                Time.deltaTime * speed
            );
        }
        else
        {
            sceneCamera.fieldOfView = Mathf.Lerp(
                sceneCamera.fieldOfView,
                fieldOfView,
                Time.deltaTime * speed
            );
        }
    }
}
