using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.InputSystem;

public class LaserToggleScript : MonoBehaviour
{

    public Sprite laserOnButtonSprite;
    public Sprite laserOffButtonSprite;
    public GameObject laserToggleButton;
    private bool isLaserOn = true;

    public InputAction laserToggleAction;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        laserToggleAction.Enable();
        laserToggleAction.performed += ctx => ToggleLaser();
        
    }

    // Update is called once per frame
    void Update()
    {

        
    }

    public void ToggleLaser()
    {
        // Implement laser toggle functionality here
        if (isLaserOn)
        {
            StartCoroutine(StopLaser());
            laserToggleButton.GetComponent<Image>().sprite = laserOffButtonSprite;
            isLaserOn = false;
            
        } else
        {
            StartCoroutine(StartLaser());
            laserToggleButton.GetComponent<Image>().sprite = laserOnButtonSprite;
            isLaserOn = true;
        }
        
    }

    IEnumerator StartLaser()
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/laser/on", "POST");
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
            Debug.Log("Laser turned on!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    IEnumerator StopLaser()
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/laser/off", "POST");
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
            Debug.Log("Laser turned off!");
            Debug.Log(request.downloadHandler.text);
        }
    }


}
