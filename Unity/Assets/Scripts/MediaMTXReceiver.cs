using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using Unity.WebRTC;

public class MediaMtxWhepReceiver : MonoBehaviour
{
    [SerializeField] public string whepUrl = "http://10.0.0.1:8889/stream/whep";
    [SerializeField] private RawImage targetImage;
    [SerializeField] private float retryDelaySeconds = 2f;

    private RTCPeerConnection peer;
    private VideoStreamTrack remoteVideoTrack;
    private Coroutine webRtcUpdateCoroutine;
    private Coroutine connectCoroutine;

    private bool isShuttingDown;
    private bool isConnected;
    private bool isReconnecting;

    private void Start()
    {
        webRtcUpdateCoroutine = StartCoroutine(WebRTC.Update());
        connectCoroutine = StartCoroutine(ConnectionLoop());
    }

    private IEnumerator ConnectionLoop()
    {
        while (!isShuttingDown)
        {
            isConnected = false;

            yield return StartCoroutine(CleanupPeer());

            yield return StartCoroutine(TryStartReceiving());

            if (isConnected || isShuttingDown)
                yield break;

            Debug.Log($"WHEP connect failed. Retrying in {retryDelaySeconds} seconds...");
            yield return new WaitForSeconds(retryDelaySeconds);
        }
    }

    private IEnumerator TryStartReceiving()
    {
        RTCConfiguration config = default;
        peer = new RTCPeerConnection(ref config);

        peer.OnConnectionStateChange = state =>
        {
            Debug.Log($"Connection state: {state}");

            if (state == RTCPeerConnectionState.Connected)
            {
                isConnected = true;
                isReconnecting = false;
            }
            else if (
                state == RTCPeerConnectionState.Failed ||
                state == RTCPeerConnectionState.Disconnected ||
                state == RTCPeerConnectionState.Closed)
            {
                if (!isShuttingDown && !isReconnecting)
                {
                    isReconnecting = true;
                    Debug.LogWarning("Connection lost. Restarting connection loop...");
                    StartCoroutine(RestartConnectionLoop());
                }
            }
        };

        peer.OnIceConnectionChange = state =>
        {
            Debug.Log($"ICE connection state: {state}");

            if (
                state == RTCIceConnectionState.Failed ||
                state == RTCIceConnectionState.Disconnected ||
                state == RTCIceConnectionState.Closed)
            {
                if (!isShuttingDown && !isReconnecting)
                {
                    isReconnecting = true;
                    Debug.LogWarning("ICE connection lost. Restarting connection loop...");
                    StartCoroutine(RestartConnectionLoop());
                }
            }
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
                    if (targetImage != null)
                        targetImage.texture = tex;
                };

                if (targetImage != null && remoteVideoTrack.Texture != null)
                    targetImage.texture = remoteVideoTrack.Texture;
            }
        };

        var transceiverInit = new RTCRtpTransceiverInit
        {
            direction = RTCRtpTransceiverDirection.SendRecv
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

        yield return new WaitUntil(() =>
            peer != null && peer.GatheringState == RTCIceGatheringState.Complete);

        if (peer == null)
            yield break;

        string localSdp = peer.LocalDescription.sdp;
        Debug.Log("Local SDP:\n" + localSdp);

        using (var req = new UnityWebRequest(whepUrl, UnityWebRequest.kHttpVerbPOST))
        {
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(localSdp));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/sdp");
            req.SetRequestHeader("Accept", "application/sdp");

            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"WHEP request failed: {req.responseCode} {req.error}\n{req.downloadHandler.text}");
                yield break;
            }

            RTCSessionDescription answerDesc = new RTCSessionDescription
            {
                type = RTCSdpType.Answer,
                sdp = req.downloadHandler.text
            };
            Debug.Log("Remote SDP:\n" + req.downloadHandler.text);
            var setRemoteOp = peer.SetRemoteDescription(ref answerDesc);
            yield return setRemoteOp;

            if (setRemoteOp.IsError)
            {
                Debug.LogError($"SetRemoteDescription failed: {setRemoteOp.Error.message}");
                yield break;
            }
        }

        Debug.Log("Connected to stream");
        isConnected = true;
        isReconnecting = false;
    }

    private IEnumerator RestartConnectionLoop()
    {
        yield return StartCoroutine(CleanupPeer());

        if (!isShuttingDown)
        {
            yield return new WaitForSeconds(retryDelaySeconds);

            if (connectCoroutine != null)
                StopCoroutine(connectCoroutine);

            connectCoroutine = StartCoroutine(ConnectionLoop());
        }
    }

    private IEnumerator CleanupPeer()
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

        if (targetImage != null)
            targetImage.texture = null;

        yield return null;
    }

    private void OnDestroy()
    {
        isShuttingDown = true;

        if (connectCoroutine != null)
        {
            StopCoroutine(connectCoroutine);
            connectCoroutine = null;
        }

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