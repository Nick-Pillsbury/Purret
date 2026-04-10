using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using UnityEngine.InputSystem;
using System;
using System.Data.Common;

[Serializable]
public class ChatMessage
{
    public string user;
    public string text;
}

[Serializable]
public class ChatHistoryResponse
{
    public IdentifierCase id;
    public string user;
    public string text;
    public string timestamp;
}

[Serializable]
public class ChatHistoryResponseWrapper
{
    public ChatHistoryResponse[] messages;
}

public class ChatClient : MonoBehaviour
{
    public CameraMovementScript cameraMovementScript;
    public TMP_InputField inputField;
    public TMP_Text chatText;
    public string apiBaseUrl = "http://10.0.0.1:8000";

    public static string playerName;

    private string lastMessageId;

    public InputAction submitAction;

    public bool enteringText = false;

    void Start()
    {
        StartCoroutine(PollChat());
    }

    public void OnSendButton()
    {
        var text = inputField.text.Trim();
        if (string.IsNullOrEmpty(text)) return;
        StartCoroutine(SendChat(text));
        inputField.text = "";
    }

    IEnumerator SendChat(string text)
    {
        ChatMessage message = new ChatMessage { user = playerName, text = text };
        var requestBody = JsonUtility.ToJson(message);
        var request = new UnityWebRequest(apiBaseUrl + "/chat/send", "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(requestBody);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Chat send failed: " + request.error);
        }
    }

    IEnumerator PollChat()
    {
        while (true)
        {
            using var request = UnityWebRequest.Get(apiBaseUrl + "/chat/history");
            yield return request.SendWebRequest();
            // print("Polling chat history...");
            if (request.result == UnityWebRequest.Result.Success)
            {
                // print("Chat history response: " + request.downloadHandler.text);
                chatText.text = "";
                var response = request.downloadHandler.text;
                var wrapper = JsonUtility.FromJson<ChatHistoryResponseWrapper>("{\"messages\":" + response + "}");
                if (wrapper?.messages != null)
                {
                    foreach (var msg in wrapper.messages)
                    {
                        chatText.text += $"{msg.user}: {msg.text}\n";
                    }
                }
                else
                {
                    Debug.LogWarning("Chat history parse returned no messages.");
                }
            }
            yield return new WaitForSeconds(0.5f);
        }
    }

    IEnumerator ClearChat() {
        var request = new UnityWebRequest(apiBaseUrl + "/chat/clear", "POST");
        request.downloadHandler = new DownloadHandlerBuffer();
        request.uploadHandler = new UploadHandlerRaw(new byte[0]);
        request.SetRequestHeader("Content-Type", "application/json");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Chat clear failed: " + request.error);
        }
    }

    public void ClearChatHistory()
    {
        print("Clearing chat history...");
        StartCoroutine(ClearChat());
    }
    private void OnEnable()
    {
        submitAction.Enable();
        submitAction.performed += OnSubmitAction;
    }

    private void OnDisable()
    {
        submitAction.performed -= OnSubmitAction;
        submitAction.Disable();
    }

    private void OnSubmitAction(InputAction.CallbackContext context)
    {
        if (enteringText)
        {
            OnSendButton();
        }
    }

    public void ToggleEnteringText()
    {
        enteringText = !enteringText;
        if (enteringText)
        {
            cameraMovementScript.enabled = false;
        } else
        {
            cameraMovementScript.enabled = true;
        }
    }
}