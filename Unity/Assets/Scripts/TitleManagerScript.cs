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

        // placeholder
        invalidIPText.SetActive(true);
        invalidIPText.GetComponentInChildren<TextMeshProUGUI>().text = "Error! Unable to connect to Purret!";
        
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
