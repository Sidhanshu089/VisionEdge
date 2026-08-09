from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from backend.streaming.video_tracker import TensorRTVideoTrack
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer


app = FastAPI(title="VisionEdge WebRTC Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VIDEO_PATH = Path("assets/videos/input/Video1.mp4")

peer_connections = set()


@app.get("/")
def root():
    return {
        "message": "VisionEdge WebRTC Backend Running"
    }


@app.post("/offer")
async def offer(request: Request):

    params = await request.json()

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    pc = RTCPeerConnection()
    peer_connections.add(pc)

    print("✅ WebRTC peer connection created.")

    player = MediaPlayer(str(VIDEO_PATH))

    if player.video:
        processed_track = TensorRTVideoTrack(player.video)

        pc.addTrack(processed_track)

        print("✅ TensorRT video track added.")

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print("✅ WebRTC answer created.")

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }