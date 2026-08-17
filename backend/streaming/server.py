from backend.config import (
    VIDEO_PATH,
    VIDEO_SOURCE,
    RTSP_URL,
    MODEL_NAME,
    MODEL_VERSION,
    INPUT_WIDTH,
    INPUT_HEIGHT,
    CONFIDENCE_THRESHOLD,
    TARGET_FPS,
)
from backend.monitoring.gpu_monitor import get_gpu_metrics

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

from backend.streaming.video_tracker import TensorRTVideoTrack


app = FastAPI(title="VisionEdge WebRTC Server")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------------------------------------------------------
# RUNTIME STATE
# ---------------------------------------------------------

peer_connections = set()
active_track = None
active_player = None


# ---------------------------------------------------------
# HEALTH CHECK(PREVIUOSLY)
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "VisionEdge WebRTC Backend Running",
        "status": "healthy",
    }

# ---------------------------------------------------------
# HEALTH CHECK(NEW)
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "VisionEdge Backend"
    }


# ---------------------------------------------------------
# SYSTEM STATUS
# ---------------------------------------------------------

@app.get("/status")
def status():

    gpu = get_gpu_metrics()

    return {
        "backend": "online",
        "streaming": active_track is not None,
        "video_source": VIDEO_SOURCE,
        "active_peers": len(peer_connections),

        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,

        "inference_engine": "TensorRT",

        "input_size": f"{INPUT_WIDTH}x{INPUT_HEIGHT}",
        "confidence_threshold": CONFIDENCE_THRESHOLD,

        "target_fps": TARGET_FPS,

        "tensorRT": (
            "ready"
            if active_track is not None
            else "idle"
        ),
        "gpu": gpu,
    }

# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

@app.get("/metrics")
def metrics():

    if active_track is None:
        return {
            "active": False
        }

    return {
        "active": True,
        **active_track.latest_metrics
    }

# ---------------------------------------------------------
# BENCHMARK
# ---------------------------------------------------------
    
@app.get("/benchmark")
def benchmark():

    if active_track is None:
        return {
            "active": False,
            "samples": 0,
            "gpu_samples": 0,
        }

    # -------------------------------------------------
    # PIPELINE BENCHMARK HISTORY
    # -------------------------------------------------

    history = list(active_track.benchmark_history)

    # -------------------------------------------------
    # GPU BENCHMARK HISTORY
    # -------------------------------------------------

    gpu_history = list(active_track.gpu_benchmark_history)

    def statistics(key, data):

        values = [sample[key] for sample in data]

        return {
            "average": round(sum(values) / len(values), 2),
            "minimum": round(min(values), 2),
            "maximum": round(max(values), 2),
        }

    # -------------------------------------------------
    # PIPELINE STATISTICS
    # -------------------------------------------------

    pipeline_result = {}

    if history:

        pipeline_result = {
            "samples": len(history),

            "fps": statistics(
                "fps",
                history
            ),

            "preprocess_ms": statistics(
                "preprocess",
                history
            ),

            "tensorrt_ms": statistics(
                "tensorrt",
                history
            ),

            "postprocess_ms": statistics(
                "postprocess",
                history
            ),

            "total_ms": statistics(
                "total",
                history
            ),

            "detections": statistics(
                "detections",
                history
            ),
        }

    # -------------------------------------------------
    # GPU STATISTICS
    # -------------------------------------------------

    gpu_result = {}

    if gpu_history:

        gpu_result = {
            "samples": len(gpu_history),

            "utilization": statistics(
                "gpu_utilization",
                gpu_history
            ),

            "memory_used_mb": statistics(
                "memory_used",
                gpu_history
            ),

            "temperature_c": statistics(
                "temperature",
                gpu_history
            ),

            "power_w": statistics(
                "power",
                gpu_history
            ),
        }

    # -------------------------------------------------
    # FINAL BENCHMARK RESPONSE
    # -------------------------------------------------

    return {
        "active": True,

        "pipeline": pipeline_result,

        "gpu": gpu_result,
    }


# ---------------------------------------------------------
# WEBRTC OFFER
# ---------------------------------------------------------

@app.post("/offer")
async def offer(request: Request):

    global active_track
    global active_player

    params = await request.json()

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    pc = RTCPeerConnection()

    peer_connections.add(pc)

    active_track = None
    active_player = None

    print("✅ WebRTC peer connection created.")

    # -----------------------------------------------------
    # CONNECTION STATE HANDLING
    # -----------------------------------------------------

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():

        global active_track
        global active_player

        print(
            f"WebRTC connection state: "
            f"{pc.connectionState}"
        )

        if pc.connectionState in {
            "failed",
            "closed",
            "disconnected",
        }:

            print("🛑 WebRTC connection closed.")

            peer_connections.discard(pc)

            if active_track is not None:
                active_track.stop()
                active_track = None

            if active_player is not None:
                active_player.audio = None
                active_player.video = None
                active_player = None

            await pc.close()

    # -----------------------------------------------------
    # VIDEO SOURCE
    # -----------------------------------------------------

    if not VIDEO_PATH.exists():

        raise FileNotFoundError(
            f"Video file not found: {VIDEO_PATH}"
        )

    if VIDEO_SOURCE == "file":

        player = MediaPlayer(str(VIDEO_PATH))

    elif VIDEO_SOURCE == "rtsp":

        if not RTSP_URL:
            raise RuntimeError(
                "RTSP_URL is not configured."
            )

        player = MediaPlayer(
            RTSP_URL,
            options={
                "rtsp_transport": "tcp"
            }
        )

    else:

        raise RuntimeError(
            f"Unsupported video source: {VIDEO_SOURCE}"
        )

    active_player = player

    # -----------------------------------------------------
    # TENSORRT TRACK
    # -----------------------------------------------------

    if player.video:

        processed_track = TensorRTVideoTrack(
            player.video
        )

        active_track = processed_track

        pc.addTrack(processed_track)

        print("✅ TensorRT video track added.")

    else:

        raise RuntimeError(
            "Unable to create video track."
        )

    # -----------------------------------------------------
    # WEBRTC NEGOTIATION
    # -----------------------------------------------------

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()

    await pc.setLocalDescription(answer)

    print("✅ WebRTC answer created.")

    # -----------------------------------------------------
    # RETURN ANSWER
    # -----------------------------------------------------

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }