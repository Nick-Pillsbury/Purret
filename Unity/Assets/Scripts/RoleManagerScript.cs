using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using System;

[Serializable]
public class TokenResponse
{
    public string token;
}
public class RoleManagerScript : MonoBehaviour
{
    public GameObject roleUnavailableText;
    public static string token;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    IEnumerator Login(string username)
    {
        string json = "{\"username\":\"" + username + "\"}";
        var request = new UnityWebRequest("http://10.0.0.1:8000/login", "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);

        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        request.SetRequestHeader("Accept", "application/json");

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.responseCode + " " + request.error);
            Debug.Log(request.downloadHandler.text);
            roleUnavailableText.SetActive(true);
            roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The player role is currently unavailable!";
        }
        else
        {
            Debug.Log(request.downloadHandler.text);
            string tokenValue = JsonUtility.FromJson<TokenResponse>(request.downloadHandler.text).token;
            token = tokenValue;
            SceneManager.LoadScene("ControlScene");
            // parse token from JSON and store it
        }
    }

    public void TryRole(string role)
    {
        // placeholder
        
        if (role == "Player")
        {
            StartCoroutine(Login("player"));
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
