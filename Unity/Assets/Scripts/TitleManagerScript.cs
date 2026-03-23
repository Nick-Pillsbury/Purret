using System.Collections;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.Networking;
public class TitleManagerScript : MonoBehaviour
{

    public string username;
    public GameObject invalidIPText;

    public InputAction submitAction;

    public bool enteringText = false;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    void Update()
    {
        
    }

    public void TryConnect()
    {
        // StartCoroutine(StartPing());
        if (username == null || username == "")
        {
            invalidIPText.SetActive(true);
            invalidIPText.GetComponentInChildren<TextMeshProUGUI>().text = "Error! Please enter a valid username!";
            return;
        }
        StartCoroutine(SendRequest(username));
    }

    IEnumerator SendRequest(string username)
    {
        if (username == "admin")
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("RoleSelectScene");
            yield break;
        }
        UnityWebRequest www = UnityWebRequest.Post("http://10.0.0.1:8000/login", "{ \"token\": \"" + username + "\" }", "application/json");
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Successfully connected to Purret!");
            // Load the next scene or perform any necessary actions
        }
    }

    IEnumerator StartPing()
    {
        WaitForSeconds f = new WaitForSeconds(0.05f);
            Ping p = new Ping("10.0.0.1");
            while (p.isDone == false)
            {
                yield return f;
            }
            PingFinished(p);
    }

    private void PingFinished(Ping p)
    {
        if (p.time >= 0)
        {
            Debug.Log("Successfully connected to Purret!");
            // Load the next scene or perform any necessary actions
        } else
        {
            invalidIPText.SetActive(true);
            invalidIPText.GetComponentInChildren<TextMeshProUGUI>().text = "Error! Unable to connect to Purret!";
        }
    }

    public void SetUsername(string usernameInput)
    {
        username = usernameInput;
    }

    public void QuitApplication()
    {
        Application.Quit();
    }

    public void ToggleEnteringText()
    {
        enteringText = !enteringText;
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
        TryConnect();
}

}
