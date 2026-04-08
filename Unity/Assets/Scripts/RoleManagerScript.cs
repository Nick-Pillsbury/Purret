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
        UnityEngine.SceneManagement.SceneManager.LoadScene("ControlScene");
    }

    public void LoadSpectatorScene()
    {
        // Load the spectator scene
        UnityEngine.SceneManagement.SceneManager.LoadScene("SpectatorScene");
    }

}
