using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using Unity.WebRTC;

public class MediaMtxWhepReceiver : MonoBehaviour
{
    [SerializeField] public string whepUrl = "http://192.168.1.245:8889/stream/whep";
    [SerializeField] private RawImage targetImage;

    private RTCPeerConnection peer;
    private VideoStreamTrack remoteVideoTrack;
    private Coroutine webRtcUpdateCoroutine;

    private void Start()
    {
        webRtcUpdateCoroutine = StartCoroutine(WebRTC.Update());
        StartCoroutine(StartReceiving());
    }

    private IEnumerator StartReceiving()
    {
        RTCConfiguration config = default;
        peer = new RTCPeerConnection(ref config);

        peer.OnConnectionStateChange = state =>
        {
            Debug.Log($"Connection state: {state}");
        };

        peer.OnIceConnectionChange = state =>
        {
            Debug.Log($"ICE connection state: {state}");
        };

        peer.OnIceGatheringStateChange = state =>
        {
            Debug.Log($"ICE gathering state: {state}");
        };

        peer.OnTrack = e =>
        {
            Debug.Log($"Track received: {e.Track.Kind}");

            if (e.Track is VideoStreamTrack videoTrack)
            {
                remoteVideoTrack = videoTrack;

                remoteVideoTrack.OnVideoReceived += tex =>
                {
                    Debug.Log("Video frame received");
                    if (targetImage != null)
                        targetImage.texture = tex;
                };

                // Fallback in case frames are already available through Texture.
                if (targetImage != null && remoteVideoTrack.Texture != null)
                    targetImage.texture = remoteVideoTrack.Texture;
            }
        };

        var transceiverInit = new RTCRtpTransceiverInit
        {
            direction = RTCRtpTransceiverDirection.RecvOnly
        };

        peer.AddTransceiver(TrackKind.Video, transceiverInit);

        var offerOp = peer.CreateOffer();
        yield return offerOp;

        if (offerOp.IsError)
        {
            Debug.LogError($"CreateOffer failed: {offerOp.Error.message}");
            yield break;
        }

        RTCSessionDescription offerDesc = offerOp.Desc;

        var setLocalOp = peer.SetLocalDescription(ref offerDesc);
        yield return setLocalOp;

        if (setLocalOp.IsError)
        {
            Debug.LogError($"SetLocalDescription failed: {setLocalOp.Error.message}");
            yield break;
        }

        // Wait until ICE gathering is complete.
        yield return new WaitUntil(() =>
            peer.GatheringState == RTCIceGatheringState.Complete);

        string localSdp = peer.LocalDescription.sdp;

        using var req = new UnityWebRequest(whepUrl, UnityWebRequest.kHttpVerbPOST);
        req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(localSdp));
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/sdp");
        req.SetRequestHeader("Accept", "application/sdp");

        yield return req.SendWebRequest();

        if (req.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError($"WHEP request failed: {req.error}\n{req.downloadHandler.text}");
            yield break;
        }

        RTCSessionDescription answerDesc = new RTCSessionDescription
        {
            type = RTCSdpType.Answer,
            sdp = req.downloadHandler.text
        };

        var setRemoteOp = peer.SetRemoteDescription(ref answerDesc);
        yield return setRemoteOp;

        if (setRemoteOp.IsError)
        {
            Debug.LogError($"SetRemoteDescription failed: {setRemoteOp.Error.message}");
            yield break;
        }

        Debug.Log("Connected to stream");
    }

    private void OnDestroy()
    {
        if (remoteVideoTrack != null)
        {
            remoteVideoTrack.Dispose();
            remoteVideoTrack = null;
        }

        if (peer != null)
        {
            peer.Close();
            peer.Dispose();
            peer = null;
        }

        if (webRtcUpdateCoroutine != null)
        {
            StopCoroutine(webRtcUpdateCoroutine);
            webRtcUpdateCoroutine = null;
        }
    }
}