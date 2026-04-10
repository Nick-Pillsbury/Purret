using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
public class GameManagerScript : MonoBehaviour
{

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartCoroutine(StartVideoFeed("player"));

        
    }

    IEnumerator StartVideoFeed(string username)
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/camera/start", "POST");
        request.downloadHandler = new DownloadHandlerBuffer();
        request.uploadHandler = new UploadHandlerRaw(new byte[0]);
        request.SetRequestHeader("Authorization", "Bearer " + RoleManagerScript.token);
        request.SetRequestHeader("Accept", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.responseCode + " " + request.error);
            Debug.Log(request.downloadHandler.text);
        }
        else
        {
            Debug.Log("Camera feed started!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    IEnumerator StopVideoFeed(string username)
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/camera/stop", "POST");
        request.downloadHandler = new DownloadHandlerBuffer();
        request.uploadHandler = new UploadHandlerRaw(new byte[0]);
        request.SetRequestHeader("Authorization", "Bearer " + RoleManagerScript.token);
        request.SetRequestHeader("Accept", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.responseCode + " " + request.error);
            Debug.Log(request.downloadHandler.text);
        }
        else
        {
            Debug.Log("Camera feed stopped!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    IEnumerator Logout(string username)
    {

        UnityWebRequest www = UnityWebRequest.Post("http://10.0.0.1:8000/logout", "{ \"token\": \"" + username + "\" }", "application/json");
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            // roleUnavailableText.SetActive(true);
            // roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The player role is currently unavailable!";
        }
        else
        {
            Debug.Log("Successfully logged out!");

            SceneManager.LoadScene("RoleSelectScene");
            // Load the next scene or perform any necessary actions
        }
    }

    public void ExitToRoleSelect(string userType)
    {
        
        // Load the role selection scene
        if (userType == "Player")
        {
            StartCoroutine(StopVideoFeed("player"));
            StartCoroutine(Logout("player"));
        }
        else if (userType == "Spectator")
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("RoleSelectScene");
        }
        
        
    }

    public void ExitToMainMenu()
    {
        // Load the main menu scene
        UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu");
    }

}
