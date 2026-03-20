using System.Collections;
using TMPro;
using UnityEngine;

public class TitleManagerScript : MonoBehaviour
{
    public string username;
    public GameObject invalidIPText;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

        
    }

    public void TryConnect()
    {
        StartCoroutine(StartPing());
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
}
