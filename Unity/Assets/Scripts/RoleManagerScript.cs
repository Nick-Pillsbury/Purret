using UnityEngine;
using UnityEngine.SceneManagement;

public class RoleManagerScript : MonoBehaviour
{
    public GameObject roleUnavailableText;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    public void TryRole(string role)
    {
        // placeholder
        roleUnavailableText.SetActive(true);
        roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The " + role + " role is currently unavailable!";
        if (role == "Player")
        {
            // LoadPlayerScene();
        }
        else if (role == "Spectator")
        {
            // LoadSpectatorScene();
        }
    }

    public void ExitToMainMenu()
    {
        // placeholder
        UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu");
    }

    public void LoadPlayerScene()
    {
        // Load the player scene
        switch (Application.platform)
        {
            case RuntimePlatform.WindowsPlayer:
            case RuntimePlatform.WindowsEditor:
            case RuntimePlatform.OSXEditor:
            case RuntimePlatform.OSXPlayer:
            case RuntimePlatform.LinuxPlayer:
                UnityEngine.SceneManagement.SceneManager.LoadScene("ControlScene");
                break;
            case RuntimePlatform.IPhonePlayer:
            case RuntimePlatform.Android:
                UnityEngine.SceneManagement.SceneManager.LoadScene("MobileControlScene");
                break;
            default:
                Debug.LogError("Unsupported platform for player role.");
                break;
        }
    }

    public void LoadSpectatorScene()
    {
        // Load the spectator scene
        UnityEngine.SceneManagement.SceneManager.LoadScene("SpectatorScene");
    }

}
