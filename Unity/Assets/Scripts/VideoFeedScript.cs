using UnityEngine;
using Unity.WebRTC;

public class VideoFeedScript : MonoBehaviour
{
    private VideoStreamTrack videoStreamTrack;
    public Texture2D videoTexture;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        videoStreamTrack = new VideoStreamTrack(videoTexture);
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
