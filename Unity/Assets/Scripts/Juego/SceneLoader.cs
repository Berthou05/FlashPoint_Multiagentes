using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneLoader : MonoBehaviour
{
    // Escribe aquí el nombre EXACTO de la escena (tal como aparece en Build Settings)
    public void LoadScene(string sceneName)
    {
        SceneManager.LoadScene(sceneName);
    }

    // Atajos concretos para conectar directo a botones sin escribir el nombre en el Inspector
    public void GoToMainMenu()
    {
        SceneManager.LoadScene("MainMenu");
    }

    public void GoToSimulation()
    {
        SceneManager.LoadScene("PlaguePointSimulation");
    }
}