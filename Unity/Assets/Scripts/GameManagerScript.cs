using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
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
        if (username == "admin")
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("RoleSelectScene");
            yield break;
        }
        UnityWebRequest www = UnityWebRequest.Post("http://10.0.0.1:8000/front/camera/start", "{ \"token\": \"" + username + "\" }", "application/json");
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Successfully started video feed!");
            // Load the next scene or perform any necessary actions
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator SendRequest(string username)
    {
        if (username == "admin")
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("RoleSelectScene");
            yield break;
        }
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
            StartCoroutine(SendRequest("player"));
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
