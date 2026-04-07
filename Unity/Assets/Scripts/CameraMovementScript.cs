using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;

public class CameraMovementScript : MonoBehaviour
{
    public float currentSpeed = 50f;
    private Vector2 moveDir;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        moveDir = InputSystem.actions[ "Move" ].ReadValue<Vector2>();
        if (moveDir != Vector2.zero)
        {
            Debug.Log("Moving in direction: " + moveDir);
            StartCoroutine(MoveServo(moveDir * (currentSpeed/100f))); // Scale movement by current speed
            // Implement movement logic here, e.g., send movement commands to the robot
        }
    }

    IEnumerator MoveServo(Vector2 direction)
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/servo/move", "POST");
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
            Debug.Log("Servo moved!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    public void AdjustSpeed(float newSpeed)
    {
        // Implement speed adjustment functionality here
        currentSpeed = Mathf.Clamp(newSpeed, 0f, 100f); // Assuming speed range is 0 to 100
    }
}
