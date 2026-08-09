import { useRef, useState } from "react";

function App() {
  const videoRef = useRef(null);
  const [status, setStatus] = useState("Ready");

  async function startStream() {
    try {
      setStatus("Connecting...");

      const peerConnection = new RTCPeerConnection();

      peerConnection.ontrack = (event) => {
        console.log("🎥 Video track received");

        if (videoRef.current) {
          videoRef.current.srcObject = event.streams[0];
        }
      };

      peerConnection.addTransceiver("video", {
        direction: "recvonly",
      });

      const offer = await peerConnection.createOffer();

      await peerConnection.setLocalDescription(offer);

      const response = await fetch("http://127.0.0.1:8000/offer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const answer = await response.json();

      await peerConnection.setRemoteDescription(
        new RTCSessionDescription(answer)
      );

      setStatus("🟢 Streaming");

      console.log("✅ WebRTC connection established");
    } catch (error) {
      console.error("❌ WebRTC error:", error);
      setStatus("❌ Connection failed");
    }
  }

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "Arial",
        textAlign: "center",
      }}
    >
      <h1>VisionEdge WebRTC</h1>

      <button onClick={startStream}>
        Start Video Stream
      </button>

      <p>{status}</p>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        controls
        style={{
          width: "80%",
          maxWidth: "900px",
          marginTop: "20px",
          background: "black",
        }}
      />
    </div>
  );
}

export default App;