using UnityEngine;
using UnityEngine.SceneManagement;

public class RoleManagerScript : MonoBehaviour
{
    public GameObject roleUnavailableText;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    public void TryRole(string role)
    {
        // placeholder
        roleUnavailableText.SetActive(true);
        roleUnavailableText.GetComponentInChildren<TMPro.TextMeshProUGUI>().text = "Error! The " + role + " role is currently unavailable!";
    }

    public void ExitToMainMenu()
    {
        // placeholder
        Debug.Log("Exiting to main menu...");
    }

}
