using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Networking;

[Serializable]
public class ServoMoveRequestBody
{
    public float x;
    public float y;
    public int step;
}

public class CameraMovementScript : MonoBehaviour
{
    public float currentSpeed = 50f;
    private Vector2 moveDir;
    private bool isSending;

    private void Start()
    {
        StartCoroutine(ResetServo());
        
    }

    void FixedUpdate()
    {
        moveDir = InputSystem.actions["Move"].ReadValue<Vector2>();

        if (moveDir != Vector2.zero && !isSending)
        {
            Debug.Log("Moving in direction: " + moveDir);
            StartCoroutine(MoveServo(moveDir));
        }
    }

    IEnumerator ResetServo()
    {
        isSending = true;
        var request = new UnityWebRequest("http://10.0.0.1:8000/front/servo/reset", "POST");
        request.uploadHandler = new UploadHandlerRaw(new byte[0]);
        request.downloadHandler = new DownloadHandlerBuffer();

        request.SetRequestHeader("Authorization", "Bearer " + RoleManagerScript.token);
        request.SetRequestHeader("Content-Type", "application/json");
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

        isSending = false;
    }

    IEnumerator MoveServo(Vector2 direction)
    {
        isSending = true;

        ServoMoveRequestBody body = new ServoMoveRequestBody
        {
            x = Mathf.Clamp(direction.x, -1f, 1f),
            y = Mathf.Clamp(direction.y, -1f, 1f),
            step = Mathf.Clamp(Mathf.RoundToInt(currentSpeed / 10f), 1, 30)
        };

        string json = JsonUtility.ToJson(body);
        byte[] jsonBytes = Encoding.UTF8.GetBytes(json);

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/servo/move", "POST");
        request.uploadHandler = new UploadHandlerRaw(jsonBytes);
        request.downloadHandler = new DownloadHandlerBuffer();

        request.SetRequestHeader("Authorization", "Bearer " + RoleManagerScript.token);
        request.SetRequestHeader("Content-Type", "application/json");
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

        isSending = false;
    }

    public void AdjustSpeed(float newSpeed)
    {
        currentSpeed = Mathf.Clamp(newSpeed, 0f, 100f);
    }
}