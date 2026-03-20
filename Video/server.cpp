#include <gst/gst.h>
#include <gst/rtsp-server/rtsp-server.h>

int main(int argc, char *argv[]) {
    GMainLoop *loop;
    GstRTSPServer *server;
    GstRTSPMountPoints *mounts;
    GstRTSPMediaFactory *factory;

    gst_init(&argc, &argv);
    loop = g_main_loop_new(NULL, FALSE);

    server = gst_rtsp_server_new();
    // Bind to 0.0.0.0 so external machines (like your Unity PC) can connect
    gst_rtsp_server_set_address(server, "0.0.0.0");
    gst_rtsp_server_set_service(server, "8554");

    mounts = gst_rtsp_server_get_mount_points(server);
    factory = gst_rtsp_media_factory_new();

    /* FIXED PIPELINE STRING: 
       Note the '!' between every element and the name=pay0 at the end.
    */
    gst_rtsp_media_factory_set_launch(factory, 
        "( videotestsrc is-live=true ! video/x-raw,width=640,height=480,framerate=30/1 ! "
        "videoconvert ! x264enc tune=zerolatency bitrate=1000 speed-preset=ultrafast key-int-max=30 ! "
        "rtph264pay name=pay0 pt=96 )");

    gst_rtsp_media_factory_set_shared(factory, TRUE);
    gst_rtsp_mount_points_add_factory(mounts, "/test", factory);
    g_object_unref(mounts);

    gst_rtsp_server_attach(server, NULL);

    g_print("Stream ready at rtsp://<TARGET_IP>:8554/test\n");
    g_main_loop_run(loop);

    return 0;
}