using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class RESTAPITEST : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        UnityWebRequest request = UnityWebRequest.Get("https://jsonplaceholder.typicode.com/todos/1");
        StartCoroutine(SendRequest(request));
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator SendRequest(UnityWebRequest request)
    {
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError("Error: " + request.error);
        }
        else
        {
            string jsonResponse = request.downloadHandler.text;


            Debug.Log("Response: " + jsonResponse);
        }
    }
}
