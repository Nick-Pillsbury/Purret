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

    [Header("Laser Toggle")]
    public Sprite laserOnButtonSprite;
    public Sprite laserOffButtonSprite;
    public GameObject laserToggleButton;
    private bool isLaserOn = true;

    [Header("Recording")]
    public Sprite recordingOnSprite;
    public Sprite recordingOffSprite;
    public GameObject recordingButton;
    private bool isRecording = false;

    [Header("Speed Adjustment")]
    public float currentSpeed = 50f;

    [Header("Player Input")]
    private Vector2 moveDir;


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

    void FixedUpdate()
    {
        moveDir = InputSystem.actions[ "Move" ].ReadValue<Vector2>();
        if (moveDir != Vector2.zero)
        {
            Debug.Log("Moving in direction: " + moveDir);
            // Implement movement logic here, e.g., send movement commands to the robot
        }
    }

    IEnumerator SendRequest(string username)
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

    IEnumerator StartRecording()
    {
        UnityWebRequest www = UnityWebRequest.Post("http://10.0.0.1:8000/front/camera/record/start", "{ \"token\": \"peebo\" }", "application/json");
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            // roleUnavailableText.SetActive(true);
            // roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The player role is currently unavailable!";
        }
        else
        {
            Debug.Log("Recording started!");
            // Load the next scene or perform any necessary actions
        }
        
    }

    public void ToggleLaser()
    {
        // Implement laser toggle functionality here
        if (isLaserOn)
        {
            laserToggleButton.GetComponent<Image>().sprite = laserOffButtonSprite;
            isLaserOn = false;
        } else
        {
            laserToggleButton.GetComponent<Image>().sprite = laserOnButtonSprite;
            isLaserOn = true;
        }
        
    }

    public void ToggleRecording()
    {

        StartCoroutine(StartRecording());
        if (isRecording)
        {
            recordingButton.GetComponent<Image>().sprite = recordingOffSprite;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().text = "RECORD";
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().fontSize = 16;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().color = Color.gray;
            isRecording = false;
        } else
        {
            recordingButton.GetComponent<Image>().sprite = recordingOnSprite;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().text = "RECORDING";
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().fontSize = 14;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().color = Color.white;
            isRecording = true;
        }
        
    }

    public void AdjustSpeed(float newSpeed)
    {
        // Implement speed adjustment functionality here
        currentSpeed = Mathf.Clamp(newSpeed, 0f, 100f); // Assuming speed range is 0 to 100
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
