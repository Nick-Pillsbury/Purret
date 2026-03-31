using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
public class RoleManagerScript : MonoBehaviour
{
    public GameObject roleUnavailableText;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    IEnumerator SendRequest(string username)
    {
        if (username == "admin")
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("RoleSelectScene");
            yield break;
        }
        UnityWebRequest www = UnityWebRequest.Post("http://10.0.0.1:8000/login", "{ \"token\": \"" + username + "\" }", "application/json");
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            roleUnavailableText.SetActive(true);
            roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The player role is currently unavailable!";
        }
        else
        {
            Debug.Log("Successfully logged in as player!");
            SceneManager.LoadScene("ControlScene");
            // Load the next scene or perform any necessary actions
        }
    }

    public void TryRole(string role)
    {
        // placeholder
        
        if (role == "Player")
        {
            StartCoroutine(SendRequest("player"));
            // LoadPlayerScene();
        }
        else if (role == "Spectator")
        {
            SceneManager.LoadScene("SpectatorScene");
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
