using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
public class RecordingToggleScript : MonoBehaviour
{

    public Sprite recordingOnSprite;
    public Sprite recordingOffSprite;
    public GameObject recordingButton;
    private bool isRecording = false;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator StartRecording()
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/camera/record/start", "POST");
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
            Debug.Log("Recording started!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    IEnumerator StopRecording()
    {

        var request = new UnityWebRequest("http://10.0.0.1:8000/front/camera/record/stop", "POST");
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
            Debug.Log("Recording stopped!");
            Debug.Log(request.downloadHandler.text);
        }
    }

    public void ToggleRecording()
    {

        
        if (isRecording)
        {
            StartCoroutine(StopRecording());
            recordingButton.GetComponent<Image>().sprite = recordingOffSprite;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().text = "RECORD";
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().fontSize = 16;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().color = Color.gray;
            isRecording = false;
        } else
        {
            StartCoroutine(StartRecording());
            recordingButton.GetComponent<Image>().sprite = recordingOnSprite;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().text = "RECORDING";
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().fontSize = 14;
            recordingButton.GetComponentInChildren<TextMeshProUGUI>().color = Color.white;
            isRecording = true;
        }
        
    }

}
